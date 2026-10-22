"""Group split and frozen test set (spec annotation-pipeline AC4, AC5, A5, A6)."""

from pathlib import Path

import pytest

from aristech.datasets.manifest import ManifestRow, Split
from aristech.datasets.split import (
    FrozenSetViolation,
    freeze,
    load_frozen,
    split_by_group,
)


def _rows(groups: int = 20, per_group: int = 5, source: str = "s") -> list[ManifestRow]:
    classes = (("vespa_velutina",), ("vespa_crabro",))
    return [
        ManifestRow(
            f"{source}{g:02d}{i}", source, "p", f"{source}/g{g}", f"l{g}{i}", classes[g % 2]
        )
        for g in range(groups)
        for i in range(per_group)
    ]


def test_split_is_deterministic_and_never_splits_a_group() -> None:
    first = split_by_group(_rows(), seed=0)
    assert first == split_by_group(_rows(), seed=0)
    by_group: dict[str, set[Split]] = {}
    for row in first:
        by_group.setdefault(row.group, set()).add(row.split)
    assert all(len(splits) == 1 for splits in by_group.values())
    assert {s for splits in by_group.values() for s in splits} == {
        Split.TRAIN,
        Split.VALIDATION,
        Split.TEST,
    }


def test_split_is_stratified_by_class_set() -> None:
    rows = split_by_group(_rows(), seed=3)
    for cls in ("vespa_velutina", "vespa_crabro"):
        assert any(r.split is Split.TEST and cls in r.classes for r in rows)


def test_seed_changes_assignment() -> None:
    assert split_by_group(_rows(), seed=0) != split_by_group(_rows(), seed=1)


def test_bad_ratios_raise() -> None:
    with pytest.raises(ValueError):
        split_by_group(_rows(), seed=0, ratios=(0.9, 0.2))


def test_captive_groups_never_go_to_test() -> None:
    rows = split_by_group(_rows(source="lab"), seed=0, captive_sources=frozenset({"lab"}))
    assert all(r.split is not Split.TEST for r in rows)


def _frozen_store(tmp_path: Path) -> tuple[list[ManifestRow], Path, Path]:
    rows = split_by_group(_rows(), seed=0)
    store = tmp_path / "store"
    (store / "labels").mkdir(parents=True)
    for row in rows:
        (store / "labels" / f"{row.image_sha256}.txt").write_text(row.label_sha256)
    return rows, tmp_path / "registry", store


def test_freeze_writes_csv_digest_and_label_snapshot(tmp_path: Path) -> None:
    rows, registry, store = _frozen_store(tmp_path)
    registry.mkdir()
    frozen = freeze("test-v1", rows, registry, store)
    tests = [r for r in rows if r.split is Split.TEST]
    assert len(frozen.rows) == len(tests)
    assert len(list((registry / "test-v1-labels").iterdir())) == len(tests)
    assert load_frozen(registry / "test-v1.csv") == frozen
    with pytest.raises(FileExistsError):
        freeze("test-v1", rows, registry, store)


def test_freeze_without_test_rows_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="run split first"):
        freeze("test-v1", _rows(), tmp_path, tmp_path)


def test_edited_frozen_file_is_detected(tmp_path: Path) -> None:
    rows, registry, store = _frozen_store(tmp_path)
    registry.mkdir()
    freeze("test-v1", rows, registry, store)
    path = registry / "test-v1.csv"
    path.write_text(path.read_text()[:-2] + "x\n")
    with pytest.raises(ValueError, match="digest"):
        load_frozen(path)


def test_resplit_with_frozen_set_keeps_test_and_adds_new_groups(tmp_path: Path) -> None:
    rows, registry, store = _frozen_store(tmp_path)
    registry.mkdir()
    frozen = freeze("test-v1", rows, registry, store)
    grown = rows + _rows(groups=6, source="new")
    resplit = split_by_group(grown, seed=99, frozen=frozen)
    frozen_shas = {r.image_sha256 for r in frozen.rows}
    assert all(r.split is Split.TEST for r in resplit if r.image_sha256 in frozen_shas)


def test_violations_name_each_problem(tmp_path: Path) -> None:
    rows, registry, store = _frozen_store(tmp_path)
    registry.mkdir()
    frozen = freeze("test-v1", rows, registry, store)
    test_rows = [r for r in rows if r.split is Split.TEST]
    moved, relabelled, missing = test_rows[0], test_rows[1], test_rows[2]
    intruder = ManifestRow("zz", "s", "p", moved.group, "l", ("vespa_velutina",), Split.TRAIN)
    broken = [
        r.__class__(**{**{f: getattr(r, f) for f in r.__dataclass_fields__}, "split": Split.TRAIN})
        if r is moved
        else r.__class__(
            **{**{f: getattr(r, f) for f in r.__dataclass_fields__}, "label_sha256": "changed"}
        )
        if r is relabelled
        else r
        for r in rows
        if r is not missing
    ] + [intruder]
    problems = frozen.violations(broken)
    assert any("left test" in p for p in problems)
    assert any("label changed" in p for p in problems)
    assert any("missing" in p for p in problems)
    assert any("frozen group" in p for p in problems)


def test_split_refuses_a_broken_frozen_set(tmp_path: Path) -> None:
    rows, registry, store = _frozen_store(tmp_path)
    registry.mkdir()
    frozen = freeze("test-v1", rows, registry, store)
    with pytest.raises(FrozenSetViolation) as info:
        split_by_group(
            [r for r in rows if r.image_sha256 != frozen.rows[0].image_sha256],
            seed=0,
            frozen=frozen,
        )
    assert info.value.violations
