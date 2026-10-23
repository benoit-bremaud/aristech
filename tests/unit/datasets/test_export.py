"""YOLO view export (spec annotation-pipeline AC11, AC5)."""

import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from aristech.datasets.export import data_yaml, export_yolo_view
from aristech.datasets.manifest import ManifestRow, Split
from aristech.datasets.split import FrozenRow, FrozenSetViolation, FrozenTestSet


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


@pytest.fixture
def store(tmp_path: Path) -> Path:
    store = tmp_path / "store"
    (store / "images").mkdir(parents=True)
    (store / "labels").mkdir()
    return store


def _row(store: Path, name: str, split: Split, group: str) -> ManifestRow:
    sha = _sha(name)
    (store / "images" / f"{sha}.jpg").write_bytes(name.encode())
    label = f"0 0.5 0.5 0.1 0.1 # {name}\n"
    (store / "labels" / f"{sha}.txt").write_text(label)
    return ManifestRow(sha, "s", f"{name}.jpg", group, _sha(label), ("vespa_velutina",), split)


def _frozen(registry: Path, rows: list[ManifestRow], snapshot_text: str) -> FrozenTestSet:
    labels = registry / "test-v1-labels"
    labels.mkdir(parents=True)
    for row in rows:
        (labels / f"{row.image_sha256}.txt").write_text(snapshot_text)
    frozen_rows = tuple(
        FrozenRow(r.image_sha256, r.label_sha256, r.group, r.source_id) for r in rows
    )
    return FrozenTestSet("test-v1", frozen_rows)


def test_export_links_splits_and_uses_the_label_snapshot(store: Path, tmp_path: Path) -> None:
    train = _row(store, "a", Split.TRAIN, "g1")
    valid = _row(store, "b", Split.VALIDATION, "g2")
    test = _row(store, "c", Split.TEST, "g3")
    frozen = _frozen(tmp_path / "registry", [test], "1 0.5 0.5 0.2 0.2\n")
    out = tmp_path / "view"

    counts = export_yolo_view([train, valid, test], [frozen], store, tmp_path / "registry", out)

    assert counts == {"train": 1, "valid": 1, "test-v1": 1}
    image = out / "train" / "images" / f"{train.image_sha256}.jpg"
    assert image.is_symlink() and image.read_bytes() == b"a"
    assert (out / "valid" / "labels" / f"{valid.image_sha256}.txt").exists()
    snapshot = out / "test-v1" / "labels" / f"{test.image_sha256}.txt"
    assert snapshot.read_text() == "1 0.5 0.5 0.2 0.2\n"
    assert not (out / "train" / "images" / f"{test.image_sha256}.jpg").exists()
    assert (out / "data.yaml").read_text() == data_yaml(out)


def test_data_yaml_lists_the_four_classes_in_canonical_order(tmp_path: Path) -> None:
    text = data_yaml(tmp_path)
    assert "nc: 4" in text
    assert text.index("0: vespa_velutina") < text.index("3: other")
    assert "train: train/images" in text and "val: valid/images" in text


def test_frozen_violation_refuses_and_leaves_out_untouched(store: Path, tmp_path: Path) -> None:
    test = _row(store, "c", Split.TEST, "g3")
    frozen = _frozen(tmp_path / "registry", [test], "x\n")
    out = tmp_path / "view"
    out.mkdir()
    (out / "keep").write_text("old")
    moved = replace(test, split=Split.TRAIN)

    with pytest.raises(FrozenSetViolation, match="test-v1"):
        export_yolo_view([moved], [frozen], store, tmp_path / "registry", out)
    assert (out / "keep").read_text() == "old"


def test_missing_image_raises_before_writing(store: Path, tmp_path: Path) -> None:
    row = _row(store, "a", Split.TRAIN, "g1")
    (store / "images" / f"{row.image_sha256}.jpg").unlink()
    out = tmp_path / "view"

    with pytest.raises(FileNotFoundError, match=row.image_sha256[:12]):
        export_yolo_view([row], [], store, tmp_path / "registry", out)
    assert not out.exists()


def test_unassigned_rows_are_skipped_and_old_view_replaced(store: Path, tmp_path: Path) -> None:
    out = tmp_path / "view"
    (out / "train").mkdir(parents=True)
    (out / "train" / "stale").write_text("x")
    row = _row(store, "a", Split.UNASSIGNED, "g1")

    assert export_yolo_view([row], [], store, tmp_path / "registry", out) == {}
    assert not (out / "train").exists()
