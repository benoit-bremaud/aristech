"""Live visual detection use case."""

import logging
from dataclasses import dataclass, field
from datetime import datetime

from aristech.application.attack_episode import AttackEpisodeTracker, EpisodeRule
from aristech.application.decision import Decision, decide
from aristech.application.ports import HornetDetector, Notifier, VideoSource

_log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DetectHornetVisualConfig:
    """`confidence_threshold`: the ACT point for `decide()` (ADR-0004, ADR-0029).
    `count_threshold`: the COUNT point feeding the attack episodes (ADR-0014,
    ADR-0031); None means the ACT point. `COUNT <= ACT` must hold."""

    confidence_threshold: float = 0.5
    count_threshold: float | None = None
    episode_rule: EpisodeRule = field(default_factory=EpisodeRule)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be in [0, 1]")
        if self.count_threshold is not None and not (
            0.0 <= self.count_threshold <= self.confidence_threshold
        ):
            raise ValueError("count_threshold must be in [0, confidence_threshold]")

    @property
    def count_point(self) -> float:
        """The COUNT threshold in effect."""
        return self.confidence_threshold if self.count_threshold is None else self.count_threshold


@dataclass(frozen=True, slots=True)
class DetectionRun:
    """Outcome of a run: how many targets were acted on and abstained on
    (ADR-0009), and how many attack episodes opened. Counts, not lists: a camera
    stream never ends, so keeping every detection would grow memory without bound."""

    threats: int = 0
    abstentions: int = 0
    episodes: int = 0


class DetectHornetVisual:
    """Reads frames, runs the detector and notifies every threat (ACT) and every
    abstention (target below the threshold, ABSTAIN); other species are ignored.
    Frames with a *V. velutina* at or above the COUNT point feed the attack
    episode rule, which raises one alert per episode (ADR-0031).

    Every dependency is injected behind a port, so camera, model and notification
    channel can change without touching this use case.
    """

    def __init__(
        self,
        video: VideoSource,
        detector: HornetDetector,
        notifier: Notifier,
        config: DetectHornetVisualConfig | None = None,
    ) -> None:
        self._video = video
        self._detector = detector
        self._notifier = notifier
        self._config = config or DetectHornetVisualConfig()

    def run(self) -> DetectionRun:
        """Consume the whole source, then close it, even on error. An episode still
        open when the run stops (end of stream, interruption or error) is closed at
        the last frame seen and its summary sent."""
        threats = abstentions = episodes = 0
        tracker = AttackEpisodeTracker(self._config.episode_rule)
        last_seen: datetime | None = None
        try:
            threshold = self._config.confidence_threshold
            count_point = self._config.count_point
            for frame in self._video.frames():
                hit = False
                for detection in self._detector.detect(frame):
                    hit = hit or (detection.is_threat() and detection.confidence >= count_point)
                    decision = decide(detection, threshold)
                    if decision is Decision.ACT:
                        self._notifier.notify_detection(detection)
                        threats += 1
                    elif decision is Decision.ABSTAIN:
                        self._notifier.notify_abstention(detection)
                        abstentions += 1
                    else:
                        _log.debug("ignore %s %.2f", detection.species.value, detection.confidence)
                last_seen = frame.timestamp
                episode = tracker.observe(frame.timestamp, hit)
                if episode is not None and episode.ended is None:
                    self._notifier.notify_attack_started(episode)
                    episodes += 1
                elif episode is not None:
                    self._notifier.notify_attack_ended(episode)
        finally:
            try:
                if last_seen is not None and (ended := tracker.close(last_seen)) is not None:
                    self._notifier.notify_attack_ended(ended)
            finally:
                self._video.close()
        return DetectionRun(threats=threats, abstentions=abstentions, episodes=episodes)
