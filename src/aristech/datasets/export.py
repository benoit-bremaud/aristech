"""YOLO view of the manifest for training and scoring (ADR-0024, spec annotation-pipeline AC11).

The view links, never copies, the content-addressed store: `train/` and `valid/` hold the train
and validation rows, and each frozen set gets its own folder (`test-v1/`…) whose labels are the
committed snapshot, the yardstick every model is scored on (ADR-0020). `data.yaml` names the four
canonical classes in order. Every frozen-set check runs before anything is written.
"""

from __future__ import annotations

import shutil
from collections.abc import Sequence
from pathlib import Path

from aristech.datasets.manifest import CANONICAL_CLASSES, ManifestRow, Split
from aristech.datasets.split import FrozenSetViolation, FrozenTestSet

_FOLDERS = {Split.TRAIN: "train", Split.VALIDATION: "valid"}


def _stored_image(store: Path, image_sha: str) -> Path:
    matches = sorted((store / "images").glob(f"{image_sha}.*"))
    if not matches:
        raise FileNotFoundError(f"image {image_sha[:12]} is not in {store / 'images'}")
    return matches[0]


def _link(target: Path, link: Path) -> None:
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(target.resolve())


def data_yaml(view: Path) -> str:
    """The `data.yaml` text of a view rooted at `view` (YOLO / RF-DETR layout)."""
    names = "".join(f"  {i}: {name}\n" for i, name in enumerate(CANONICAL_CLASSES))
    return (
        f"path: {view.resolve()}\ntrain: train/images\nval: valid/images\n"
        f"nc: {len(CANONICAL_CLASSES)}\nnames:\n{names}"
    )


def export_yolo_view(
    rows: Sequence[ManifestRow],
    frozen: Sequence[FrozenTestSet],
    store: Path,
    registry: Path,
    out: Path,
) -> dict[str, int]:
    """Write the view under `out` (replaced if it exists); return the image count per folder.

    Raises `FrozenSetViolation` if `rows` break any frozen set and `FileNotFoundError` if a
    stored image is missing; in both cases `out` is left untouched.
    """
    violations = [f"{f.id}: {v}" for f in frozen for v in f.violations(rows)]
    if violations:
        raise FrozenSetViolation(violations)
    plan: list[tuple[Path, Path]] = []
    counts: dict[str, int] = {}
    for row in rows:
        folder = _FOLDERS.get(row.split)
        if folder is None:
            continue
        image = _stored_image(store, row.image_sha256)
        plan.append((image, Path(folder, "images", image.name)))
        label = f"{row.image_sha256}.txt"
        plan.append((store / "labels" / label, Path(folder, "labels", label)))
        counts[folder] = counts.get(folder, 0) + 1
    for frozen_set in frozen:
        snapshot = registry / f"{frozen_set.id}-labels"
        for frozen_row in frozen_set.rows:
            image = _stored_image(store, frozen_row.image_sha256)
            plan.append((image, Path(frozen_set.id, "images", image.name)))
            label = f"{frozen_row.image_sha256}.txt"
            plan.append((snapshot / label, Path(frozen_set.id, "labels", label)))
        counts[frozen_set.id] = len(frozen_set.rows)
    if out.exists():
        shutil.rmtree(out)
    for target, relative in plan:
        _link(target, out / relative)
    out.mkdir(parents=True, exist_ok=True)
    (out / "data.yaml").write_text(data_yaml(out), encoding="utf-8")
    return counts
