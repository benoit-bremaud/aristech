"""CLI composition-root wiring (ADR-0009): the detector gets the floor, the
use case gets the operating threshold. The vision adapters are swapped for
hand-written fakes, so neither cv2 nor torch is needed."""

import logging
from collections.abc import Iterator, Sequence
from datetime import datetime
from pathlib import Path

import pytest

from aristech.domain import BoundingBox, Detection, Species, VideoFrame
from aristech.infrastructure.vision import opencv_video_source, vespai_detector
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
    assert "1 menace(s), 1 abstention(s)" in caplog.text


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
