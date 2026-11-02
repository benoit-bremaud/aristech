"""CLI composition-root wiring (ADR-0009): the detector gets the floor, the
use case gets the operating threshold. The vision adapters are swapped for
hand-written fakes, so neither cv2 nor torch is needed."""

import logging
from collections.abc import Iterator, Sequence
from datetime import datetime
from pathlib import Path

import pytest

from aristech.domain import BoundingBox, Detection, Species, VideoFrame
from aristech.infrastructure.vision import opencv_video_source, rfdetr_detector, vespai_detector
from aristech.interface.cli import main as cli
from aristech.interface.cli.main import main


class _FakeVideo:
    def __init__(self, source: str | int) -> None:
        self.source = source

    def frames(self) -> Iterator[VideoFrame]:
        yield VideoFrame(pixels=None, width=640, height=480, timestamp=datetime(2026, 10, 16))

    def close(self) -> None:
        pass


class _FakeDetector:
    created: list[dict[str, object]] = []

    def __init__(self, **kwargs: object) -> None:
        _FakeDetector.created.append(kwargs)

    def detect(self, frame: VideoFrame) -> Sequence[Detection]:
        def det(species: Species, conf: float) -> Detection:
            return Detection(species, BoundingBox(0, 0, 10, 10), conf, frame.timestamp)

        return [
            det(Species.VESPA_VELUTINA, 0.9),
            det(Species.VESPA_VELUTINA, 0.3),
            det(Species.APIS_MELLIFERA, 0.3),
        ]


@pytest.fixture
def argv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> list[str]:
    _FakeDetector.created = []
    monkeypatch.setattr(opencv_video_source, "OpenCVVideoSource", _FakeVideo)
    monkeypatch.setattr(vespai_detector, "VespAIDetector", _FakeDetector)
    monkeypatch.setattr(rfdetr_detector, "RFDETRDetector", _FakeDetector)
    cfg = tmp_path / "config.yaml"
    cfg.write_text("app:\n  version: test\n", encoding="utf-8")
    weights = tmp_path / "w.pt"
    weights.write_text("x", encoding="utf-8")
    video = tmp_path / "clip.mp4"
    video.write_text("x", encoding="utf-8")
    return [
        "--config",
        str(cfg),
        "--logging-config",
        str(tmp_path / "none.yaml"),
        "--video",
        str(video),
        "--weights",
        str(weights),
        "--yolov5-dir",
        str(tmp_path),
    ]


def _run(argv: list[str], caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="aristech"):
        assert main([*argv, "--confidence", "0.5", "--detector-floor", "0.2"]) == 0


def test_detector_runs_at_the_floor(argv, caplog):
    _run(argv, caplog)
    assert _FakeDetector.created[0]["confidence"] == 0.2


def test_run_summary_counts_threats_and_abstentions(argv, caplog):
    _run(argv, caplog)
    assert "1 threat(s), 1 abstention(s)" in caplog.text


def test_uncertain_target_is_logged_as_abstain(argv, caplog):
    _run(argv, caplog)
    assert "abstain vespa_velutina" in caplog.text


def test_non_target_species_is_not_reported(argv, caplog):
    _run(argv, caplog)
    assert "apis_mellifera" not in caplog.text


@pytest.mark.parametrize("floor", ["0.5", "0"])
def test_floor_at_the_bounds_is_accepted(argv, floor):
    assert main([*argv, "--confidence", "0.5", "--detector-floor", floor]) == 0
    assert _FakeDetector.created[0]["confidence"] == float(floor)


def test_default_floor_is_point_one(argv):
    assert main([*argv, "--confidence", "0.5"]) == 0
    assert _FakeDetector.created[0]["confidence"] == 0.1


def test_default_floor_is_clamped_to_low_confidence(argv):
    assert main([*argv, "--confidence", "0.05"]) == 0
    assert _FakeDetector.created[0]["confidence"] == 0.05


@pytest.mark.parametrize("floor", ["0.6", "-0.1"])
def test_floor_outside_zero_to_confidence_errors(argv, floor):
    assert main([*argv, "--confidence", "0.5", "--detector-floor", floor]) == 2
    assert _FakeDetector.created == []


def test_vespai_default_threshold_is_point_five(argv, caplog):
    with caplog.at_level(logging.INFO, logger="aristech"):
        assert main(argv) == 0
    assert "Detector vespai, ACT threshold 0.5," in caplog.text
    assert "weights_path" in _FakeDetector.created[0]


def _base_argv(tmp_path: Path) -> list[str]:
    return [
        "--config",
        str(tmp_path / "config.yaml"),
        "--logging-config",
        str(tmp_path / "none.yaml"),
        "--video",
        str(tmp_path / "clip.mp4"),
        "--detector",
        "rfdetr",
    ]


@pytest.fixture
def rfdetr_argv(argv: list[str], tmp_path: Path) -> list[str]:
    checkpoint = tmp_path / "best.pth"
    checkpoint.write_bytes(b"model")
    return [*_base_argv(tmp_path), "--checkpoint", str(checkpoint)]


def test_rfdetr_runs_at_the_act_threshold_of_adr_0029(rfdetr_argv, caplog):
    with caplog.at_level(logging.INFO, logger="aristech"):
        assert main(rfdetr_argv) == 0
    assert "Detector rfdetr, ACT threshold 0.45, detector floor 0.1." in caplog.text
    assert _FakeDetector.created[0]["confidence"] == 0.1
    assert _FakeDetector.created[0]["checkpoint_path"].endswith("best.pth")
    assert "1 threat(s), 1 abstention(s)" in caplog.text


def test_rfdetr_warns_on_an_unmeasured_checkpoint(rfdetr_argv, caplog):
    with caplog.at_level(logging.INFO, logger="aristech"):
        assert main(rfdetr_argv) == 0
    assert "not the model measured by ADR-0029" in caplog.text


def test_rfdetr_measured_checkpoint_does_not_warn(rfdetr_argv, caplog, monkeypatch):
    monkeypatch.setattr(cli, "_sha256", lambda path: cli._RFDETR_MEASURED_SHA256)
    with caplog.at_level(logging.INFO, logger="aristech"):
        assert main(rfdetr_argv) == 0
    assert "not the model measured" not in caplog.text


def test_rfdetr_without_checkpoint_errors(argv, tmp_path):
    assert main(_base_argv(tmp_path)) == 2
    assert _FakeDetector.created == []


def test_rfdetr_missing_checkpoint_errors(argv, tmp_path):
    missing = str(tmp_path / "missing.pth")
    assert main([*_base_argv(tmp_path), "--checkpoint", missing]) == 2
    assert _FakeDetector.created == []


def test_run_logs_fps_and_latency(argv, caplog):
    _run(argv, caplog)
    assert "Timing: 1 frame(s), too few" in caplog.text


def test_ignored_species_is_logged_at_debug(argv, caplog):
    with caplog.at_level(logging.DEBUG, logger="aristech"):
        assert main([*argv, "--confidence", "0.5"]) == 0
    assert "ignore apis_mellifera 0.30" in caplog.text


def test_timing_with_no_frame(caplog):
    with caplog.at_level(logging.INFO, logger="aristech"):
        cli._log_timing(logging.getLogger("aristech"), [], 0.0)
    assert "Timing: 0 frame(s), too few" in caplog.text


def test_timing_percentiles(caplog):
    with caplog.at_level(logging.INFO, logger="aristech"):
        cli._log_timing(logging.getLogger("aristech"), [2.0, 0.02, 0.04, 0.03], 2.3)
    assert (
        "4 frame(s), warm-up 2.0 s, then 10.00 FPS end to end, "
        "detect latency p50 30.0 ms, p95 40.0 ms."
    ) in caplog.text


class _FailingDetector(_FakeDetector):
    def detect(self, frame: VideoFrame) -> Sequence[Detection]:
        raise RuntimeError("model load failed")


def test_timing_is_logged_even_when_detection_fails(argv, caplog, monkeypatch):
    monkeypatch.setattr(vespai_detector, "VespAIDetector", _FailingDetector)
    with caplog.at_level(logging.INFO, logger="aristech"), pytest.raises(RuntimeError):
        main(argv)
    assert "Timing: 1 frame(s), too few" in caplog.text
