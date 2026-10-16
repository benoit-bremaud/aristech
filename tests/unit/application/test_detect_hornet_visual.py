from collections.abc import Iterator, Sequence
from datetime import datetime

import pytest

from aristech.application.use_cases import DetectHornetVisual, DetectHornetVisualConfig
from aristech.domain import BoundingBox, Detection, Species, VideoFrame


class _FakeVideoSource:
    def __init__(self, frames: list[VideoFrame]) -> None:
        self._frames = frames
        self.closed = False

    def frames(self) -> Iterator[VideoFrame]:
        yield from self._frames

    def close(self) -> None:
        self.closed = True


class _ScriptedDetector:
    def __init__(self, per_frame: list[Sequence[Detection]]) -> None:
        self._per_frame = iter(per_frame)

    def detect(self, frame: VideoFrame) -> Sequence[Detection]:
        return next(self._per_frame, [])


class _RecordingNotifier:
    def __init__(self) -> None:
        self.received: list[Detection] = []
        self.abstained: list[Detection] = []

    def notify_detection(self, detection: Detection) -> None:
        self.received.append(detection)

    def notify_abstention(self, detection: Detection) -> None:
        self.abstained.append(detection)


def _frame() -> VideoFrame:
    return VideoFrame(pixels=None, width=640, height=480, timestamp=datetime(2026, 5, 19))


def _det(species: Species, confidence: float) -> Detection:
    return Detection(
        species=species,
        bbox=BoundingBox(0, 0, 10, 10),
        confidence=confidence,
        timestamp=datetime(2026, 5, 19),
    )


def test_reports_threats_and_abstentions_never_other_species():
    high = _det(Species.VESPA_VELUTINA, 0.9)
    low = _det(Species.VESPA_VELUTINA, 0.3)
    crabro = _det(Species.VESPA_CRABRO, 0.95)
    bee = _det(Species.APIS_MELLIFERA, 0.99)

    use_case = DetectHornetVisual(
        video=_FakeVideoSource([_frame()]),
        detector=_ScriptedDetector([[high, low, crabro, bee]]),
        notifier=(notifier := _RecordingNotifier()),
        config=DetectHornetVisualConfig(confidence_threshold=0.5),
    )

    result = use_case.run()

    assert result.threats == [high]
    assert result.abstentions == [low]
    assert notifier.received == [high]
    assert notifier.abstained == [low]


def test_target_exactly_at_threshold_acts():
    edge = _det(Species.VESPA_VELUTINA, 0.5)
    use_case = DetectHornetVisual(
        video=_FakeVideoSource([_frame()]),
        detector=_ScriptedDetector([[edge]]),
        notifier=(notifier := _RecordingNotifier()),
        config=DetectHornetVisualConfig(confidence_threshold=0.5),
    )
    result = use_case.run()
    assert result.threats == [edge]
    assert notifier.abstained == []


def test_returns_empty_when_no_frames():
    video = _FakeVideoSource([])
    use_case = DetectHornetVisual(
        video=video,
        detector=_ScriptedDetector([]),
        notifier=_RecordingNotifier(),
    )
    result = use_case.run()
    assert result.threats == []
    assert result.abstentions == []
    assert video.closed, "VideoSource.close() doit être appelée même sans frame"


def test_closes_video_source_on_detector_exception():
    class _BoomDetector:
        def detect(self, frame: VideoFrame) -> Sequence[Detection]:
            raise RuntimeError("boom")

    video = _FakeVideoSource([_frame()])
    use_case = DetectHornetVisual(
        video=video,
        detector=_BoomDetector(),
        notifier=_RecordingNotifier(),
    )
    with pytest.raises(RuntimeError, match="boom"):
        use_case.run()
    assert video.closed, "VideoSource.close() doit être appelée même en cas d'erreur"
