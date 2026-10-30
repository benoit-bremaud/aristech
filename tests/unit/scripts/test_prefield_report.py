"""Unit tests for scripts/prefield_report.py with fake detectors and image reader."""

import hashlib
import importlib.util
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

import pytest

from aristech.application.ports import HornetDetector
from aristech.datasets.split import FrozenRow, FrozenTestSet
from aristech.domain import BoundingBox, Detection, Species, VideoFrame

_SCRIPT = Path(__file__).parents[3] / "scripts" / "prefield_report.py"
_spec = importlib.util.spec_from_file_location("prefield_report", _SCRIPT)
assert _spec
assert _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

_LABEL = "0 0.5 0.5 0.5 0.5\n"


class _Fixed:
    """Predicts one box of `species` over the centre quarter, at confidence 0.9."""

    def __init__(self, species: Species) -> None:
        self._species = species

    def detect(self, frame: VideoFrame) -> Sequence[Detection]:
        box = BoundingBox(x=25.0, y=25.0, width=50.0, height=50.0)
        return [Detection(self._species, box, 0.9, frame.timestamp)]


def _workspace(tmp_path: Path) -> list[str]:
    registry, view = tmp_path / "registry", tmp_path / "view"
    (registry / "test-v1-labels").mkdir(parents=True)
    (view / "test-v1" / "images").mkdir(parents=True)
    (view / "test-v1" / "labels").mkdir()
    sha = hashlib.sha256(b"img").hexdigest()
    label_sha = hashlib.sha256(_LABEL.encode()).hexdigest()
    (registry / "test-v1-labels" / f"{sha}.txt").write_text(_LABEL)
    frozen = FrozenTestSet("test-v1", (FrozenRow(sha, label_sha, "g", "s"),))
    (registry / "test-v1.csv").write_text(frozen.csv_text())
    (registry / "test-v1.sha256").write_text(frozen.digest() + "\n")
    (registry / "manifest.csv").write_text("header\n")
    (view / "test-v1" / "images" / f"{sha}.jpg").write_bytes(b"img")
    (view / "test-v1" / "labels" / f"{sha}.txt").write_text(_LABEL)
    for name in ("rf.pth", "va.pt"):
        (tmp_path / name).write_bytes(name.encode())
    (tmp_path / "yolov5").mkdir()
    return [
        "--registry", str(registry), "--view", str(view),
        "--rfdetr-weights", str(tmp_path / "rf.pth"), "--vespai-weights", str(tmp_path / "va.pt"),
        "--yolov5-dir", str(tmp_path / "yolov5"), "--out", str(tmp_path / "report.md"),
    ]  # fmt: skip


@pytest.fixture(autouse=True)
def _fake_reader(monkeypatch: pytest.MonkeyPatch) -> None:
    def collect(detector: HornetDetector, base: Path, class_map: object, *, splits: tuple[str]):
        from aristech.evaluation import collect_samples

        return collect_samples(
            detector,
            base,
            _mod.CLASS_MAP,
            splits=splits,
            image_reader=lambda path: (None, 100, 100),
            timestamp=datetime(2026, 10, 23, tzinfo=UTC),
        )

    monkeypatch.setattr(_mod, "collect_samples", collect)


def test_report_puts_both_detectors_side_by_side_with_provenance(tmp_path: Path) -> None:
    factories = {
        "RF-DETR": lambda floor: _Fixed(Species.VESPA_VELUTINA),
        "VespAI": lambda floor: _Fixed(Species.VESPA_CRABRO),
    }
    assert _mod.main(_workspace(tmp_path), factories=factories) == 0
    text = (tmp_path / "report.md").read_text()
    assert "test-v1 (1 images)" in text
    assert hashlib.sha256(b"rf.pth").hexdigest() in text
    assert "CC BY-NC-SA" in text
    row = next(line for line in text.splitlines() if line.startswith("| vespa_velutina"))
    assert row == "| vespa_velutina | 1.000 | 1.000 | 1/0/0 | 0.000 | 0.000 | 0/0/1 |"
    assert text.count("### conf") == 2


def test_floor_is_the_lowest_threshold(tmp_path: Path) -> None:
    floors: list[float] = []

    def make(floor: float) -> HornetDetector:
        floors.append(floor)
        return _Fixed(Species.VESPA_VELUTINA)

    args = [*_workspace(tmp_path), "--thresholds", "0.8,0.3"]
    assert _mod.main(args, factories={"A": make}) == 0
    assert floors == [0.3]


@pytest.mark.parametrize(
    ("extra", "message"),
    [(["--thresholds", "0.5,1.5"], "thresholds"), (["--test-set", "test-v9"], "test-v9")],
)
def test_bad_input_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], extra: list[str], message: str
) -> None:
    assert _mod.main([*_workspace(tmp_path), *extra], factories={}) == 2
    assert message in capsys.readouterr().err


def test_missing_weights_exit_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    args = _workspace(tmp_path)
    (tmp_path / "rf.pth").unlink()
    assert _mod.main(args, factories={}) == 2
    assert "RF-DETR weights" in capsys.readouterr().err


def test_a_stale_view_exits_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    args = _workspace(tmp_path)
    label = next((tmp_path / "view" / "test-v1" / "labels").iterdir())
    label.write_text("1 0.5 0.5 0.5 0.5\n")
    (tmp_path / "view" / "test-v1" / "images" / "extra.jpg").write_bytes(b"x")

    assert _mod.main(args, factories={}) == 2
    err = capsys.readouterr().err
    assert "stale" in err
    assert "not in test-v1" in err
    assert "label differs" in err


def test_missing_report_directory_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    args = _workspace(tmp_path)
    args[-1] = str(tmp_path / "nowhere" / "report.md")
    assert _mod.main(args, factories={}) == 2
    assert "report directory" in capsys.readouterr().err
