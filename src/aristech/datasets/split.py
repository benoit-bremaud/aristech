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
import shutil
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path

from aristech.datasets.manifest import ManifestRow, Split

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
        frozen_shas = {r.image_sha256 for r in self.rows}
        for row in by_sha.values():
            if row.group in self.groups and row.split in (Split.TRAIN, Split.VALIDATION):
                if row.image_sha256 not in frozen_shas:
                    found.append(
                        f"{row.image_sha256[:12]} of frozen group {row.group} in {row.split.value}"
                    )
        return found


def split_by_group(
    rows: Sequence[ManifestRow],
    *,
    seed: int,
    ratios: tuple[float, float] = (0.70, 0.15),
    frozen: FrozenTestSet | None = None,
    captive_sources: frozenset[str] = frozenset(),
) -> list[ManifestRow]:
    """Assign every row a split by group; raise `FrozenSetViolation` if `frozen` is broken.

    `ratios` are (train, validation); test takes the rest. Within each stratum (groups sharing
    the same set of classes), groups are shuffled with `seed` and each goes to the split furthest
    below its target image share. Frozen groups go to test; captive groups never do (spec A6).
    """
    train_ratio, validation_ratio = ratios
    if train_ratio < 0 or validation_ratio < 0 or train_ratio + validation_ratio > 1:
        raise ValueError("ratios must be non-negative and sum to at most 1")
    groups: dict[str, list[ManifestRow]] = defaultdict(list)
    for row in rows:
        groups[row.group].append(row)
    frozen_groups = frozen.groups if frozen else frozenset()
    assignment = {g: Split.TEST for g in groups if g in frozen_groups}

    strata: dict[frozenset[str], list[str]] = defaultdict(list)
    for name, members in groups.items():
        if name not in assignment:
            strata[frozenset(c for r in members for c in r.classes)].append(name)
    targets = {Split.TRAIN: train_ratio, Split.VALIDATION: validation_ratio}
    targets[Split.TEST] = 1 - train_ratio - validation_ratio
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
    if frozen is not None:
        problems = frozen.violations(result)
        if problems:
            raise FrozenSetViolation(problems)
    return result


def freeze(
    set_id: str, rows: Iterable[ManifestRow], registry_dir: Path, store: Path
) -> FrozenTestSet:
    """Freeze the test rows as `<registry_dir>/<set_id>.csv` + a label snapshot + its digest.

    Raises `FileExistsError` if that version exists: a frozen set is never rewritten.
    """
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
    labels_dir.mkdir(parents=True)
    for row in test_rows:
        shutil.copyfile(
            store / "labels" / f"{row.image_sha256}.txt", labels_dir / f"{row.image_sha256}.txt"
        )
    target.write_text(frozen.csv_text(), encoding="utf-8")
    (registry_dir / f"{set_id}.sha256").write_text(
        f"{frozen.digest()}  {set_id}.csv\n", encoding="utf-8"
    )
    return frozen


def load_frozen(path: Path) -> FrozenTestSet:
    """Read a frozen set and check it against its recorded digest (`ValueError` if tampered)."""
    with path.open(newline="", encoding="utf-8") as handle:
        try:
            rows = tuple(FrozenRow(**{k: r[k] for k in _FIELDS}) for r in csv.DictReader(handle))
        except KeyError as exc:
            raise ValueError(f"{path} lacks column {exc}: it was edited") from exc
    frozen = FrozenTestSet(id=path.stem, rows=rows)
    recorded = path.with_suffix(".sha256").read_text(encoding="utf-8").split()[0]
    if recorded != frozen.digest():
        raise ValueError(f"{path} does not match its recorded digest: it was edited")
    return frozen
