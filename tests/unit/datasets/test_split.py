"""Group split and frozen test set (spec annotation-pipeline AC4, AC5, A5, A6)."""

import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from aristech.datasets.manifest import ManifestRow, Split
from aristech.datasets.split import (
    FrozenSetViolation,
    FrozenTestSet,
    discover_frozen,
    freeze,
    load_frozen,
    split_by_group,
)

_CLASSES = (("vespa_velutina",), ("vespa_crabro",))


def _label_hash(sha: str) -> str:
    return hashlib.sha256(f"label of {sha}\n".encode()).hexdigest()


def _rows(groups: int = 20, per_group: int = 5, source: str = "s") -> list[ManifestRow]:
    return [
        ManifestRow(sha, source, "p", f"{source}/g{g}", _label_hash(sha), _CLASSES[g % 2])
        for g in range(groups)
        for i in range(per_group)
        for sha in [f"{source}{g:02d}{i}"]
    ]


def _splits_by_group(rows: list[ManifestRow]) -> dict[str, set[Split]]:
    by_group: dict[str, set[Split]] = {}
    for row in rows:
        by_group.setdefault(row.group, set()).add(row.split)
    return by_group


def test_split_is_deterministic_and_never_splits_a_group() -> None:
    first = split_by_group(_rows(), seed=0)
    assert first == split_by_group(_rows(), seed=0)
    by_group = _splits_by_group(first)
    assert all(len(splits) == 1 for splits in by_group.values())
    assert set().union(*by_group.values()) == {Split.TRAIN, Split.VALIDATION, Split.TEST}


def test_unequal_groups_stay_whole() -> None:
    rows = [ManifestRow(f"big{i}", "s", "p", "s/big", "l", _CLASSES[0]) for i in range(40)] + _rows(
        groups=6, per_group=2
    )
    by_group = _splits_by_group(split_by_group(rows, seed=5))
    assert all(len(splits) == 1 for splits in by_group.values())


def test_split_is_stratified_by_class_set() -> None:
    rows = split_by_group(_rows(), seed=3)
    for cls in ("vespa_velutina", "vespa_crabro"):
        assert any(r.split is Split.TEST and cls in r.classes for r in rows)


def test_seed_changes_assignment() -> None:
    assert split_by_group(_rows(), seed=0) != split_by_group(_rows(), seed=1)


@pytest.mark.parametrize("ratios", [(0.9, 0.2), (-0.1, 0.5)])
def test_bad_ratios_raise(ratios: tuple[float, float]) -> None:
    with pytest.raises(ValueError, match="ratios"):
        split_by_group(_rows(), seed=0, ratios=ratios)


def test_captive_groups_never_go_to_test_but_others_do() -> None:
    rows = _rows(source="lab") + _rows(source="pub")
    result = split_by_group(rows, seed=0, captive_sources=frozenset({"lab"}))
    assert all(r.split is not Split.TEST for r in result if r.source_id == "lab")
    assert any(r.split is Split.TEST for r in result if r.source_id == "pub")


def _store(tmp_path: Path, rows: list[ManifestRow]) -> Path:
    store = tmp_path / "store"
    (store / "labels").mkdir(parents=True, exist_ok=True)
    for row in rows:
        (store / "labels" / f"{row.image_sha256}.txt").write_text(f"label of {row.image_sha256}\n")
    return store


@pytest.fixture
def frozen_setup(tmp_path: Path) -> tuple[list[ManifestRow], Path, FrozenTestSet]:
    rows = split_by_group(_rows(), seed=0)
    registry = tmp_path / "registry"
    registry.mkdir()
    return rows, registry, freeze("test-v1", rows, registry, _store(tmp_path, rows))


def test_freeze_writes_csv_digest_and_label_snapshot(
    tmp_path: Path, frozen_setup: tuple[list[ManifestRow], Path, FrozenTestSet]
) -> None:
    rows, registry, frozen = frozen_setup
    tests = [r for r in rows if r.split is Split.TEST]
    assert {r.image_sha256 for r in frozen.rows} == {r.image_sha256 for r in tests}
    for row in tests:
        snapshot = registry / "test-v1-labels" / f"{row.image_sha256}.txt"
        assert hashlib.sha256(snapshot.read_bytes()).hexdigest() == row.label_sha256
    assert load_frozen(registry / "test-v1.csv") == frozen
    assert discover_frozen(registry) == [frozen]
    with pytest.raises(FileExistsError):
        freeze("test-v1", rows, registry, tmp_path / "store")


def test_freeze_without_test_rows_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="run split first"):
        freeze("test-v1", _rows(), tmp_path, tmp_path)


def test_freeze_with_stale_store_writes_nothing(tmp_path: Path) -> None:
    rows = split_by_group(_rows(), seed=0)
    store = _store(tmp_path, rows)
    victim = next(r for r in rows if r.split is Split.TEST)
    (store / "labels" / f"{victim.image_sha256}.txt").unlink()
    with pytest.raises(ValueError, match="missing or stale"):
        freeze("test-v1", rows, tmp_path, store)
    assert list(tmp_path.glob("test-v1*")) == []


@pytest.mark.parametrize("tamper", ["csv", "digest_missing", "snapshot"])
def test_tampered_frozen_set_is_detected(
    frozen_setup: tuple[list[ManifestRow], Path, FrozenTestSet], tamper: str
) -> None:
    _, registry, frozen = frozen_setup
    path = registry / "test-v1.csv"
    if tamper == "csv":
        path.write_text(path.read_text()[:-2] + "x\n")
    elif tamper == "digest_missing":
        (registry / "test-v1.sha256").unlink()
    else:
        (registry / "test-v1-labels" / f"{frozen.rows[0].image_sha256}.txt").write_text(
            "0 1 1 1 1\n"
        )
    with pytest.raises(ValueError):
        load_frozen(path)


def test_resplit_keeps_frozen_test_and_assigns_new_groups(
    frozen_setup: tuple[list[ManifestRow], Path, FrozenTestSet],
) -> None:
    rows, _, frozen = frozen_setup
    newcomer = ManifestRow("late", "s", "p", frozen.rows[0].group, "l", _CLASSES[0])
    grown = rows + _rows(groups=6, source="new") + [newcomer]
    resplit = {r.image_sha256: r for r in split_by_group(grown, seed=99, frozen=[frozen])}
    assert all(resplit[f.image_sha256].split is Split.TEST for f in frozen.rows)
    assert resplit["late"].split is Split.TEST
    assert all(r.split is not Split.UNASSIGNED for r in resplit.values())


def _violations(frozen: FrozenTestSet, rows: list[ManifestRow]) -> list[str]:
    return frozen.violations(rows)


def test_violation_image_left_test(
    frozen_setup: tuple[list[ManifestRow], Path, FrozenTestSet],
) -> None:
    rows, _, frozen = frozen_setup
    sha = frozen.rows[0].image_sha256
    problems = _violations(
        frozen, [replace(r, split=Split.TRAIN) if r.image_sha256 == sha else r for r in rows]
    )
    assert len(problems) == 1 and "left test" in problems[0]


def test_violation_label_changed(
    frozen_setup: tuple[list[ManifestRow], Path, FrozenTestSet],
) -> None:
    rows, _, frozen = frozen_setup
    sha = frozen.rows[0].image_sha256
    problems = _violations(
        frozen, [replace(r, label_sha256="x") if r.image_sha256 == sha else r for r in rows]
    )
    assert len(problems) == 1 and "label changed" in problems[0]


def test_violation_image_missing(
    frozen_setup: tuple[list[ManifestRow], Path, FrozenTestSet],
) -> None:
    rows, _, frozen = frozen_setup
    sha = frozen.rows[0].image_sha256
    problems = _violations(frozen, [r for r in rows if r.image_sha256 != sha])
    assert len(problems) == 1 and "missing" in problems[0]


def test_violation_new_image_of_frozen_group_in_train(
    frozen_setup: tuple[list[ManifestRow], Path, FrozenTestSet],
) -> None:
    rows, _, frozen = frozen_setup
    intruder = ManifestRow("zz", "s", "p", frozen.rows[0].group, "l", _CLASSES[0], Split.TRAIN)
    problems = _violations(frozen, [*rows, intruder])
    assert len(problems) == 1 and "frozen group" in problems[0]


def test_split_refuses_a_broken_frozen_set(
    frozen_setup: tuple[list[ManifestRow], Path, FrozenTestSet],
) -> None:
    rows, _, frozen = frozen_setup
    remaining = [r for r in rows if r.image_sha256 != frozen.rows[0].image_sha256]
    with pytest.raises(FrozenSetViolation) as info:
        split_by_group(remaining, seed=0, frozen=[frozen])
    assert len(info.value.violations) == 1
