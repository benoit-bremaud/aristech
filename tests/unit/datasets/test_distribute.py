"""Unit tests of the file distribution helper (real FS, under tmp_path)."""

from pathlib import Path

from aristech.datasets.distribute import distribute_files


def test_distribute_files_splits_70_20_10(tmp_path: Path):
    source = tmp_path / "source"
    train = tmp_path / "train"
    validation = tmp_path / "validation"
    test = tmp_path / "test"
    source.mkdir()

    for i in range(10):
        (source / f"image_{i}.jpg").touch()

    counts = distribute_files(
        source,
        train,
        validation,
        test,
        train_ratio=0.7,
        validation_ratio=0.2,
        extensions=(".jpg",),
        seed=0,
    )

    assert counts == (7, 2, 1)
    assert len(list(train.iterdir())) == 7
    assert len(list(validation.iterdir())) == 2
    assert len(list(test.iterdir())) == 1


def test_distribute_files_empty_source_returns_zeros(tmp_path: Path):
    source = tmp_path / "source"
    source.mkdir()
    counts = distribute_files(
        source,
        tmp_path / "t",
        tmp_path / "v",
        tmp_path / "x",
    )
    assert counts == (0, 0, 0)
