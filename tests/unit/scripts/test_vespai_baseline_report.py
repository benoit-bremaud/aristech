"""Unit tests for scripts/vespai_baseline_report.py (fake detector, no torch)."""

import importlib.util
from collections.abc import Sequence
from pathlib import Path

import pytest

from aristech.application.ports import HornetDetector
from aristech.domain import BoundingBox, Detection, Species, VideoFrame

_SCRIPT = Path(__file__).parents[3] / "scripts" / "vespai_baseline_report.py"
_spec = importlib.util.spec_from_file_location("vespai_baseline_report", _SCRIPT)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


class _FakeDetector:
    """Returns one velutina box (conf 0.6) at the centre of a 100x100 image; counts calls."""

    def __init__(self) -> None:
        self.calls = 0
        self.floor = -1.0

    def detect(self, frame: VideoFrame) -> Sequence[Detection]:
        self.calls += 1
        box = BoundingBox(x=40, y=40, width=20, height=20)  # pixels, 100x100 image
        return [
            Detection(
                species=Species.VESPA_VELUTINA,
                bbox=box,
                confidence=0.6,
                timestamp=frame.timestamp,
            )
        ]


@pytest.fixture
def dataset(tmp_path: Path) -> Path:
    for split in ("train", "valid", "test"):
        (tmp_path / split / "images").mkdir(parents=True)
        (tmp_path / split / "labels").mkdir(parents=True)
    # Two test images, each with one velutina box at the centre.
    for name in ("a", "b"):
        (tmp_path / "test" / "images" / f"{name}.jpg").write_bytes(b"")
        (tmp_path / "test" / "labels" / f"{name}.txt").write_text("1 0.5 0.5 0.2 0.2\n")
    return tmp_path


def _run(dataset: Path, tmp_path: Path, *extra: str) -> tuple[int, _FakeDetector]:
    weights = tmp_path / "w.pt"
    weights.write_bytes(b"")
    fake = _FakeDetector()

    def factory(_w: str, _y: str, floor: float) -> HornetDetector:
        fake.floor = floor
        return fake

    argv = ["--weights", str(weights), "--yolov5-dir", str(tmp_path), "--dataset", str(dataset)]
    return _mod.main([*argv, *extra], detector_factory=factory), fake


@pytest.fixture(autouse=True)
def _fake_reader(monkeypatch: pytest.MonkeyPatch) -> None:
    import aristech.evaluation.runner as runner

    monkeypatch.setattr(runner, "_default_image_reader", lambda _p: (None, 100, 100))


def test_scores_each_threshold_from_one_detector_pass(
    dataset: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, fake = _run(dataset, tmp_path)
    out = capsys.readouterr().out
    assert code == 0
    assert fake.calls == 2  # two images, one pass, two thresholds
    assert fake.floor == 0.5  # lowest threshold
    assert "Images: 2 · ground-truth boxes: 2" in out
    assert "| vespa_velutina | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |" in out  # conf 0.5
    assert "| vespa_velutina | 0 | 0 | 2 | 0.000 | 0.000 | 0.000 |" in out  # conf 0.8


@pytest.mark.parametrize(
    "extra",
    [
        ("--class-map", "0:not_a_species"),
        ("--class-map", "0"),
        ("--thresholds", "1.5"),
        ("--thresholds", "abc"),
    ],
)
def test_bad_arguments_exit_2(dataset: Path, tmp_path: Path, extra: tuple[str, str]) -> None:
    assert _run(dataset, tmp_path, *extra)[0] == 2


@pytest.mark.parametrize(
    ("flag", "message"),
    [
        ("--dataset", "Dataset not found"),
        ("--weights", "Weights not found"),
        ("--yolov5-dir", "YOLOv5 directory not found"),
    ],
)
def test_missing_path_exits_2(
    dataset: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture, flag: str, message: str
) -> None:
    # argparse keeps the last occurrence, so this overrides the valid path.
    code, fake = _run(dataset, tmp_path, flag, str(tmp_path / "nope"))
    assert code == 2
    assert message in caplog.text
    assert fake.calls == 0


def test_missing_split_exits_2_before_running_detector(
    dataset: Path, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    code, fake = _run(dataset, tmp_path, "--splits", "holdout")
    assert code == 2
    assert "Split not found" in caplog.text
    assert fake.floor == -1.0  # detector never built


def test_defaults_score_all_splits_with_hornet_class_map(
    dataset: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (dataset / "train" / "images" / "c.jpg").write_bytes(b"")
    (dataset / "train" / "labels" / "c.txt").write_text("0 0.5 0.5 0.2 0.2\n")  # crabro
    assert _run(dataset, tmp_path)[0] == 0
    out = capsys.readouterr().out
    assert "splits: train valid test" in out
    assert "(IoU ≥ 0.50)" in out
    assert "| vespa_crabro | 0 | 0 | 1 |" in out  # class 0 = crabro, missed
