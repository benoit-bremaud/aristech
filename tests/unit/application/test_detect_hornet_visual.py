from collections.abc import Iterator, Sequence
from datetime import datetime, timedelta

import pytest

from aristech.application.attack_episode import AttackEpisode, EpisodeRule
from aristech.application.use_cases import (
    DetectHornetVisual,
    DetectHornetVisualConfig,
    DetectionRun,
)
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
        self.started: list[AttackEpisode] = []
        self.ended: list[AttackEpisode] = []

    def notify_detection(self, detection: Detection) -> None:
        self.received.append(detection)

    def notify_abstention(self, detection: Detection) -> None:
        self.abstained.append(detection)

    def notify_attack_started(self, episode: AttackEpisode) -> None:
        self.started.append(episode)

    def notify_attack_ended(self, episode: AttackEpisode) -> None:
        self.ended.append(episode)


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

    assert result == DetectionRun(threats=1, abstentions=1)
    assert notifier.received == [high]
    assert notifier.abstained == [low]


def test_target_exactly_at_threshold_acts():
    edge = _det(Species.VESPA_VELUTINA, 0.5)
    notifier = _RecordingNotifier()
    use_case = DetectHornetVisual(
        video=_FakeVideoSource([_frame()]),
        detector=_ScriptedDetector([[edge]]),
        notifier=notifier,
        config=DetectHornetVisualConfig(confidence_threshold=0.5),
    )
    result = use_case.run()
    assert result == DetectionRun(threats=1, abstentions=0)
    assert notifier.received == [edge]
    assert notifier.abstained == []


def test_returns_empty_when_no_frames():
    video = _FakeVideoSource([])
    use_case = DetectHornetVisual(
        video=video,
        detector=_ScriptedDetector([]),
        notifier=_RecordingNotifier(),
    )
    result = use_case.run()
    assert result == DetectionRun()
    assert video.closed, "VideoSource.close() must run even with no frame"


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
    assert video.closed, "VideoSource.close() must run even on error"


def _frames(count: int) -> list[VideoFrame]:
    t0 = datetime(2026, 11, 2)
    return [
        VideoFrame(pixels=None, width=640, height=480, timestamp=t0 + timedelta(seconds=i))
        for i in range(count)
    ]


def _episode_run(per_frame, count_threshold=0.15):
    notifier = _RecordingNotifier()
    use_case = DetectHornetVisual(
        video=_FakeVideoSource(_frames(len(per_frame))),
        detector=_ScriptedDetector(per_frame),
        notifier=notifier,
        config=DetectHornetVisualConfig(
            confidence_threshold=0.45,
            count_threshold=count_threshold,
            episode_rule=EpisodeRule(min_hit_frames=3),
        ),
    )
    return use_case.run(), notifier


def test_one_attack_alert_per_episode_and_a_summary_at_end_of_stream():
    hornet = _det(Species.VESPA_VELUTINA, 0.2)
    result, notifier = _episode_run([[hornet, hornet]] * 20)
    assert result.episodes == 1
    assert len(notifier.started) == 1
    assert len(notifier.ended) == 1 and notifier.ended[0].hit_frames == 20


def test_detections_below_count_point_and_non_targets_never_count():
    below = _det(Species.VESPA_VELUTINA, 0.1)
    crabro = _det(Species.VESPA_CRABRO, 0.99)
    bee = _det(Species.APIS_MELLIFERA, 0.99)
    result, notifier = _episode_run([[below, crabro, bee]] * 20)
    assert result.episodes == 0
    assert notifier.started == [] and notifier.ended == []


def test_count_point_defaults_to_the_act_point():
    config = DetectHornetVisualConfig(confidence_threshold=0.45)
    assert config.count_point == 0.45


@pytest.mark.parametrize("count", [0.5, -0.1])
def test_count_point_outside_zero_to_act_is_rejected(count):
    with pytest.raises(ValueError):
        DetectHornetVisualConfig(confidence_threshold=0.45, count_threshold=count)
