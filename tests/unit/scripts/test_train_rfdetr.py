"""Unit tests for scripts/train_rfdetr.py with a fake trainer (no rfdetr, no GPU)."""

import hashlib
import importlib.util
from pathlib import Path

import pytest

from aristech.datasets.manifest import ManifestRow, Split, write_manifest
from aristech.datasets.split import FrozenRow, FrozenTestSet

_SCRIPT = Path(__file__).parents[3] / "scripts" / "train_rfdetr.py"
_spec = importlib.util.spec_from_file_location("train_rfdetr", _SCRIPT)
assert _spec
assert _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

_HEADER = "id,name,url,version,licence,attribution,retrieved,group_rule,captive\n"


def _workspace(tmp_path: Path, licence: str = "CC-BY-4.0") -> list[str]:
    registry, store = tmp_path / "registry", tmp_path / "store"
    registry.mkdir()
    (store / "images").mkdir(parents=True)
    (store / "labels").mkdir()
    (registry / "licences.csv").write_text(_HEADER + f"ok,OK,u,1,{licence},by X,d,stem,false\n")
    sha = hashlib.sha256(b"a").hexdigest()
    (store / "images" / f"{sha}.jpg").write_bytes(b"a")
    (store / "labels" / f"{sha}.txt").write_text("0 0.5 0.5 0.1 0.1\n")
    row = ManifestRow(sha, "ok", "a.jpg", "ok/a", "l", ("vespa_velutina",), Split.TRAIN)
    write_manifest(registry / "manifest.csv", [row])
    return [
        "--registry", str(registry), "--store", str(store),
        "--view", str(tmp_path / "view"), "--output", str(tmp_path / "run"), "--epochs", "2",
    ]  # fmt: skip


def test_exports_trains_and_prints_the_checkpoint_hash(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    calls: list[tuple[Path, Path, int]] = []

    def trainer(view: Path, output: Path, epochs: int) -> None:
        calls.append((view, output, epochs))
        output.mkdir()
        (output / _mod.BEST_CHECKPOINT).write_bytes(b"weights")

    assert _mod.main(_workspace(tmp_path), trainer=trainer) == 0
    assert calls == [(tmp_path / "view", tmp_path / "run", 2)]
    assert (tmp_path / "view" / "train" / "images").is_dir()
    assert hashlib.sha256(b"weights").hexdigest() in capsys.readouterr().out


def test_refused_licence_exits_2_without_training(tmp_path: Path) -> None:
    def trainer(view: Path, output: Path, epochs: int) -> None:
        raise AssertionError("must not train")

    assert _mod.main(_workspace(tmp_path, licence="CC-BY-NC-4.0"), trainer=trainer) == 2


def test_missing_checkpoint_exits_1(tmp_path: Path) -> None:
    assert _mod.main(_workspace(tmp_path), trainer=lambda view, output, epochs: None) == 1


def test_edited_frozen_set_exits_2_without_training(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    args = _workspace(tmp_path)
    registry = tmp_path / "registry"
    (registry / "test-v1.csv").write_text("image_sha256,label_sha256,group,source_id\n")
    (registry / "test-v1.sha256").write_text("not-the-digest\n")

    assert _mod.main(args, trainer=lambda view, output, epochs: None) == 2
    assert "digest" in capsys.readouterr().err


def test_frozen_image_in_train_exits_2_without_training(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    args = _workspace(tmp_path)
    registry = tmp_path / "registry"
    sha = hashlib.sha256(b"a").hexdigest()
    empty_label = hashlib.sha256(b"").hexdigest()
    frozen = FrozenTestSet("test-v1", (FrozenRow(sha, empty_label, "ok/a", "ok"),))
    (registry / "test-v1.csv").write_text(frozen.csv_text())
    (registry / "test-v1.sha256").write_text(frozen.digest() + "\n")
    (registry / "test-v1-labels").mkdir()
    (registry / "test-v1-labels" / f"{sha}.txt").write_text("")

    assert _mod.main(args, trainer=lambda view, output, epochs: None) == 2
    assert "left test" in capsys.readouterr().err
