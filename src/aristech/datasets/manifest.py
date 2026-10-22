"""Dataset manifest: one committed row per image, no pixels (ADR-0019, spec annotation-pipeline).

Import hashes each image, remaps the source's class ids to the canonical ones (ADR-0018), writes
the image and its canonical YOLO label into a content-addressed store (`<sha256>.<ext>`,
`<sha256>.txt`, git-ignored) and returns manifest rows carrying the group key (ADR-0020).
"""

from __future__ import annotations

import csv
import hashlib
import re
import shutil
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path

from aristech.datasets.registry import Source
from aristech.domain.capture import SegmentMetadata

CANONICAL_CLASSES = ("vespa_velutina", "vespa_crabro", "apis_mellifera", "other")
"""Canonical YOLO class ids, by position (ADR-0018); `other` is `Species.UNKNOWN`."""

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")

_ROBOFLOW_SUFFIX = re.compile(r"_(jpe?g|png)\.rf\.[0-9a-f]+$", re.IGNORECASE)
_FRAME_INDEX = re.compile(r"_\d+$")
_FIELDS = ("image_sha256", "source_id", "source_path", "group", "label_sha256", "classes", "split")


class Split(str, Enum):
    """Where an image is used."""

    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"
    UNASSIGNED = "unassigned"


@dataclass(frozen=True, slots=True)
class ManifestRow:
    """One image of the database."""

    image_sha256: str
    source_id: str
    source_path: str
    group: str
    label_sha256: str
    classes: tuple[str, ...]
    split: Split = Split.UNASSIGNED


def group_key(source: Source, file_stem: str) -> str:
    """Group of an image: frames of one photo or video must never be split across sets.

    `stem` drops a Roboflow export suffix (`<orig>_jpg.rf.<hash>`), so augmented copies stay
    together; `video` also drops a trailing frame index (`MAH00001_000003` → `MAH00001`).
    """
    stem = _ROBOFLOW_SUFFIX.sub("", file_stem)
    if source.group_rule == "video":
        stem = _FRAME_INDEX.sub("", stem)
    return f"{source.id}/{stem}"


def group_for_capture(metadata: SegmentMetadata) -> str:
    """Group of a C1 frame: one hive on one UTC day (ADR-0020, spec AC6)."""
    return f"own/{metadata.hive_id}/{metadata.start_utc.date().isoformat()}"


def remap_labels(lines: Iterable[str], class_map: Mapping[int, int]) -> list[str]:
    """Rewrite YOLO lines with canonical class ids; raise `ValueError` on an unmapped class."""
    remapped: list[str] = []
    unmapped: set[int] = set()
    for raw in lines:
        parts = raw.split()
        if not parts:
            continue
        try:
            class_id = int(parts[0])
        except ValueError as exc:
            raise ValueError(f"malformed label line {raw!r}") from exc
        if class_id not in class_map:
            unmapped.add(class_id)
            continue
        target = class_map[class_id]
        if not 0 <= target < len(CANONICAL_CLASSES):
            raise ValueError(f"class map target {target} outside 0..{len(CANONICAL_CLASSES) - 1}")
        remapped.append(" ".join([str(target), *parts[1:]]))
    if unmapped:
        raise ValueError(f"unmapped source classes: {sorted(unmapped)} (extend --class-map)")
    return remapped


def import_yolo_source(
    source: Source, root: Path, class_map: Mapping[int, int], store: Path
) -> list[ManifestRow]:
    """Import every `<split>/images/<name>` (with `<split>/labels/<stem>.txt`) under `root`.

    An image without a label file has no object (empty label). A file seen twice (same hash,
    other name) yields one row per copy so `merge_rows` can join their groups; the first copy's
    label is stored. Rows come back sorted by hash then path. Evaluation on a frozen version
    reads its committed label snapshot, never this store (ADR-0020).
    """
    images_dir, labels_dir = store / "images", store / "labels"
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)
    rows: list[ManifestRow] = []
    stored_shas: set[str] = set()
    for image in sorted(root.rglob("*")):
        if image.suffix.lower() not in IMAGE_EXTENSIONS or image.parent.name != "images":
            continue
        label_file = image.parent.parent / "labels" / f"{image.stem}.txt"
        source_lines = (
            label_file.read_text(encoding="utf-8").splitlines() if label_file.exists() else []
        )
        try:
            remapped = remap_labels(source_lines, class_map)
        except ValueError as exc:
            raise ValueError(f"{label_file}: {exc}") from exc
        label_text = "".join(f"{line}\n" for line in remapped)
        image_sha = hashlib.sha256(image.read_bytes()).hexdigest()
        if image_sha not in stored_shas:
            stored_shas.add(image_sha)
            stored = images_dir / f"{image_sha}{image.suffix.lower()}"
            if not stored.exists():
                shutil.copyfile(image, stored)
            (labels_dir / f"{image_sha}.txt").write_text(label_text, encoding="utf-8")
        ids = {int(line.split()[0]) for line in label_text.splitlines()}
        rows.append(
            ManifestRow(
                image_sha256=image_sha,
                source_id=source.id,
                source_path=image.relative_to(root).as_posix(),
                group=group_key(source, image.stem),
                label_sha256=hashlib.sha256(label_text.encode()).hexdigest(),
                classes=tuple(CANONICAL_CLASSES[i] for i in sorted(ids)),
            )
        )
    return sorted(rows, key=lambda r: (r.image_sha256, r.source_path))


def merge_rows(
    existing: Iterable[ManifestRow], incoming: Iterable[ManifestRow]
) -> list[ManifestRow]:
    """Add `incoming` to `existing`, one row per image hash (spec A3).

    A known image keeps its row (label hash refreshed by a later copy). Groups that share any
    image are joined (union-find, the first-seen group name wins), so no copy or neighbouring
    frame of a test image can land in train under another group name.
    """
    parent: dict[str, str] = {}
    seen: dict[str, int] = {}

    def find(group: str) -> str:
        seen.setdefault(group, len(seen))
        parent.setdefault(group, group)
        while parent[group] != group:
            parent[group] = parent[parent[group]]
            group = parent[group]
        return group

    kept: dict[str, ManifestRow] = {}
    for row in [*existing, *incoming]:
        find(row.group)
        known = kept.get(row.image_sha256)
        if known is None:
            kept[row.image_sha256] = row
            continue
        root_known, root_new = find(known.group), find(row.group)
        if root_known != root_new:
            first, later = sorted((root_known, root_new), key=seen.__getitem__)
            parent[later] = first
        kept[row.image_sha256] = replace(known, label_sha256=row.label_sha256, classes=row.classes)
    return sorted(
        (replace(row, group=find(row.group)) for row in kept.values()),
        key=lambda r: r.image_sha256,
    )


def read_manifest(path: Path) -> list[ManifestRow]:
    """Read `manifest.csv`; a missing file is an empty manifest."""
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            ManifestRow(
                image_sha256=row["image_sha256"],
                source_id=row["source_id"],
                source_path=row["source_path"],
                group=row["group"],
                label_sha256=row["label_sha256"],
                classes=tuple(c for c in row["classes"].split(";") if c),
                split=Split(row["split"]),
            )
            for row in csv.DictReader(handle)
        ]


def write_manifest(path: Path, rows: Iterable[ManifestRow]) -> None:
    """Write `manifest.csv` sorted by image hash (stable diffs)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(_FIELDS)
        for row in sorted(rows, key=lambda r: r.image_sha256):
            writer.writerow(
                [
                    row.image_sha256,
                    row.source_id,
                    row.source_path,
                    row.group,
                    row.label_sha256,
                    ";".join(row.classes),
                    row.split.value,
                ]
            )
