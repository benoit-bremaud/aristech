"""Group split and frozen test set (ADR-0020, spec annotation-pipeline AC4, AC5).

Groups, never images, are assigned to train / validation / test, deterministically from a seed
and stratified on the set of classes a group contains. A frozen test set pins its images and
label hashes; any assignment that would move them, or put a frozen group in train, is refused.
"""

from __future__ import annotations

import csv
import hashlib
import io
import random
import re
import shutil
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path

from aristech.datasets.manifest import ManifestRow, Split

_SET_ID = re.compile(r"test-v[1-9][0-9]*")
_FIELDS = ("image_sha256", "label_sha256", "group", "source_id")


class FrozenSetViolation(ValueError):
    """An assignment breaks a frozen test set; `violations` names each offending image."""

    def __init__(self, violations: Sequence[str]) -> None:
        super().__init__(f"{len(violations)} frozen-set violation(s): " + "; ".join(violations[:5]))
        self.violations = list(violations)


@dataclass(frozen=True, slots=True)
class FrozenRow:
    """One frozen test image."""

    image_sha256: str
    label_sha256: str
    group: str
    source_id: str


@dataclass(frozen=True, slots=True)
class FrozenTestSet:
    """An immutable test-set version (`test-v1`, `test-v2`…)."""

    id: str
    rows: tuple[FrozenRow, ...]

    @property
    def groups(self) -> frozenset[str]:
        return frozenset(row.group for row in self.rows)

    def csv_text(self) -> str:
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow(_FIELDS)
        for r in sorted(self.rows, key=lambda r: r.image_sha256):
            writer.writerow([r.image_sha256, r.label_sha256, r.group, r.source_id])
        return buffer.getvalue()

    def digest(self) -> str:
        """SHA-256 of the canonical CSV text: the set's identity in every report."""
        return hashlib.sha256(self.csv_text().encode()).hexdigest()

    def violations(self, rows: Iterable[ManifestRow]) -> list[str]:
        """Every way `rows` break this frozen set (empty list = compatible)."""
        by_sha = {row.image_sha256: row for row in rows}
        found: list[str] = []
        for frozen in self.rows:
            row = by_sha.get(frozen.image_sha256)
            if row is None:
                found.append(f"{frozen.image_sha256[:12]} missing from the manifest")
            elif row.split is not Split.TEST:
                found.append(f"{frozen.image_sha256[:12]} left test ({row.split.value})")
            elif row.label_sha256 != frozen.label_sha256:
                found.append(f"{frozen.image_sha256[:12]} label changed: freeze a new version")
        frozen_groups = self.groups_in(by_sha.values())
        frozen_shas = {r.image_sha256 for r in self.rows}
        found += [
            f"{row.image_sha256[:12]} of frozen group {row.group} in {row.split.value}"
            for row in by_sha.values()
            if row.group in frozen_groups
            and row.split in (Split.TRAIN, Split.VALIDATION)
            and row.image_sha256 not in frozen_shas
        ]
        return found

    def groups_in(self, rows: Iterable[ManifestRow]) -> frozenset[str]:
        """Frozen group names plus the current group of every frozen image (groups may merge)."""
        shas = {r.image_sha256 for r in self.rows}
        return self.groups | {row.group for row in rows if row.image_sha256 in shas}


def split_by_group(
    rows: Sequence[ManifestRow],
    *,
    seed: int,
    ratios: tuple[float, float] = (0.70, 0.15),
    frozen: Sequence[FrozenTestSet] = (),
    captive_sources: frozenset[str] = frozenset(),
) -> list[ManifestRow]:
    """Assign every row a split by group; raise `FrozenSetViolation` if any `frozen` set breaks.

    `ratios` are (train, validation); test takes the rest. Within each stratum (groups sharing
    the same set of classes), groups are shuffled with `seed` and each goes to the split furthest
    below its target image share. Frozen groups go to test; captive groups never do (spec A6).
    Once a frozen set exists, the other groups go to train or validation only (ratios
    renormalised): the test split stays the frozen set, and new test images need a new version.
    """
    train_ratio, validation_ratio = ratios
    if train_ratio < 0 or validation_ratio < 0 or train_ratio + validation_ratio > 1:
        raise ValueError("ratios must be non-negative and sum to at most 1")
    groups: dict[str, list[ManifestRow]] = defaultdict(list)
    for row in rows:
        groups[row.group].append(row)
    frozen_groups = frozenset().union(*(f.groups_in(rows) for f in frozen))
    assignment = {g: Split.TEST for g in groups if g in frozen_groups}

    strata: dict[frozenset[str], list[str]] = defaultdict(list)
    for name, members in groups.items():
        if name not in assignment:
            strata[frozenset(c for r in members for c in r.classes)].append(name)
    targets = {Split.TRAIN: train_ratio, Split.VALIDATION: validation_ratio}
    targets[Split.TEST] = 1 - train_ratio - validation_ratio
    if frozen_groups:
        kept = train_ratio + validation_ratio
        if kept == 0:
            raise ValueError("ratios must leave room for train or validation once a set is frozen")
        targets = {Split.TRAIN: train_ratio / kept, Split.VALIDATION: validation_ratio / kept}
    rng = random.Random(seed)
    for stratum in sorted(strata, key=sorted):
        names = sorted(strata[stratum])
        rng.shuffle(names)
        total = sum(len(groups[n]) for n in names)
        filled = dict.fromkeys(targets, 0)
        for name in names:
            captive = any(r.source_id in captive_sources for r in groups[name])
            allowed = [s for s in targets if not (captive and s is Split.TEST)]
            split = max(allowed, key=lambda s: targets[s] * total - filled[s])
            assignment[name] = split
            filled[split] += len(groups[name])

    result = [replace(row, split=assignment[row.group]) for row in rows]
    problems = [p for f in frozen for p in f.violations(result)]
    if problems:
        raise FrozenSetViolation(problems)
    return result


def freeze(
    set_id: str, rows: Iterable[ManifestRow], registry_dir: Path, store: Path
) -> FrozenTestSet:
    """Freeze the test rows as `<registry_dir>/<set_id>.csv` + a label snapshot + its digest.

    Raises `FileExistsError` if that version exists: a frozen set is never rewritten, and
    `ValueError` if `set_id` is not `test-v<N>` (only those are discovered and enforced by split).
    """
    if not _SET_ID.fullmatch(set_id):
        raise ValueError(f"frozen set id must look like test-v1, got {set_id!r}")
    target = registry_dir / f"{set_id}.csv"
    labels_dir = registry_dir / f"{set_id}-labels"
    if target.exists() or labels_dir.exists():
        raise FileExistsError(f"{target} already frozen; freeze a new version instead")
    test_rows = [r for r in rows if r.split is Split.TEST]
    if not test_rows:
        raise ValueError("no test rows to freeze: run split first")
    frozen = FrozenTestSet(
        id=set_id,
        rows=tuple(
            FrozenRow(r.image_sha256, r.label_sha256, r.group, r.source_id) for r in test_rows
        ),
    )
    for row in test_rows:
        label = store / "labels" / f"{row.image_sha256}.txt"
        if _sha256(label) != row.label_sha256:
            raise ValueError(f"{label} is missing or stale: re-import before freezing")
    staging = registry_dir / f".{set_id}-labels.tmp"
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)
    for row in test_rows:
        shutil.copyfile(
            store / "labels" / f"{row.image_sha256}.txt", staging / f"{row.image_sha256}.txt"
        )
    staging.rename(labels_dir)
    target.write_text(frozen.csv_text(), encoding="utf-8")
    (registry_dir / f"{set_id}.sha256").write_text(
        f"{frozen.digest()}  {set_id}.csv\n", encoding="utf-8"
    )
    return frozen


def _sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def discover_frozen(registry_dir: Path) -> list[FrozenTestSet]:
    """Load every `test-v*.csv` of the registry: a split must respect all of them, always."""
    return [load_frozen(path) for path in sorted(registry_dir.glob("test-v*.csv"))]


def load_frozen(path: Path) -> FrozenTestSet:
    """Read a frozen set; `ValueError` if the CSV, its digest file or its label snapshot changed."""
    with path.open(newline="", encoding="utf-8") as handle:
        try:
            rows = tuple(FrozenRow(**{k: r[k] for k in _FIELDS}) for r in csv.DictReader(handle))
        except KeyError as exc:
            raise ValueError(f"{path} lacks column {exc}: it was edited") from exc
    frozen = FrozenTestSet(id=path.stem, rows=rows)
    digest_file = path.with_suffix(".sha256")
    if not digest_file.is_file():
        raise ValueError(f"{digest_file} is missing: {path} cannot be trusted")
    if digest_file.read_text(encoding="utf-8").split()[0] != frozen.digest():
        raise ValueError(f"{path} does not match its recorded digest: it was edited")
    labels_dir = path.with_name(f"{path.stem}-labels")
    for row in rows:
        if _sha256(labels_dir / f"{row.image_sha256}.txt") != row.label_sha256:
            raise ValueError(f"label snapshot of {row.image_sha256[:12]} in {labels_dir} changed")
    return frozen
