"""Unit tests for scripts/dataset.py (temporary files, no real images)."""

import importlib.util
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).parents[3] / "scripts" / "dataset.py"
_spec = importlib.util.spec_from_file_location("dataset_cli", _SCRIPT)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

_HEADER = "id,name,url,version,licence,attribution,retrieved,group_rule,captive\n"


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    registry = tmp_path / "registry"
    registry.mkdir()
    (registry / "licences.csv").write_text(
        _HEADER
        + "ok,OK,u,1,CC-BY-4.0,by X,2026-10-19,video,false\nnc,NC,u,1,CC-BY-NC-4.0,x,d,stem,false\n"
    )
    for video in range(10):
        for frame in range(3):
            split = "train"
            for sub in ("images", "labels"):
                (tmp_path / "export" / split / sub).mkdir(parents=True, exist_ok=True)
            stem = f"V{video}_{frame:06d}_jpg.rf.{video}{frame}"
            (tmp_path / "export" / split / "images" / f"{stem}.jpg").write_bytes(
                f"{video}-{frame}".encode()
            )
            (tmp_path / "export" / split / "labels" / f"{stem}.txt").write_text(
                f"{video % 2} 0.5 0.5 0.1 0.1\n"
            )
    return tmp_path


def _run(ws: Path, *args: str) -> int:
    return int(_mod.main(["--registry", str(ws / "registry"), "--store", str(ws / "store"), *args]))


def _import(ws: Path, source: str = "ok", class_map: str = "0:1,1:0") -> int:
    return _run(
        ws, "import", "--source", source, "--dir", str(ws / "export"), "--class-map", class_map
    )


def test_import_split_freeze_happy_path(
    workspace: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _import(workspace) == 0
    assert _run(workspace, "split", "--seed", "0") == 0
    assert _run(workspace, "freeze", "--id", "test-v1") == 0
    out = capsys.readouterr().out
    assert "imported 30 images" in out and "froze test-v1" in out
    frozen = workspace / "registry" / "test-v1.csv"
    assert _run(workspace, "split", "--seed", "7", "--frozen", str(frozen)) == 0


def test_refused_licence_exits_2_and_writes_nothing(
    workspace: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _import(workspace, source="nc") == 2
    assert "allowed" in capsys.readouterr().err
    assert not (workspace / "registry" / "manifest.csv").exists()


def test_unmapped_class_exits_2(workspace: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert _import(workspace, class_map="0:1") == 2
    assert "unmapped" in capsys.readouterr().err


def test_bad_class_map_is_a_usage_error(workspace: Path) -> None:
    with pytest.raises(SystemExit) as info:
        _import(workspace, class_map="zero:one")
    assert info.value.code == 2


def test_missing_dir_exits_2(workspace: Path) -> None:
    assert (
        _run(
            workspace,
            "import",
            "--source",
            "ok",
            "--dir",
            str(workspace / "nope"),
            "--class-map",
            "0:1",
        )
        == 2
    )


def test_refreeze_and_frozen_violation_exit_2(
    workspace: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _import(workspace)
    _run(workspace, "split", "--seed", "0")
    _run(workspace, "freeze", "--id", "test-v1")
    assert _run(workspace, "freeze", "--id", "test-v1") == 2
    manifest = workspace / "registry" / "manifest.csv"
    lines = manifest.read_text().splitlines()
    first_test = next(line for line in lines if line.endswith(",test"))
    manifest.write_text("\n".join(line for line in lines if line != first_test) + "\n")
    assert _run(workspace, "split", "--frozen", str(workspace / "registry" / "test-v1.csv")) == 2
    assert "violation:" in capsys.readouterr().err
