"""Live visual detection use case."""

import logging
from dataclasses import dataclass, field
from datetime import datetime

from aristech.application.attack_episode import (
    AttackEpisode,
    AttackEpisodeTracker,
    EpisodeRule,
)
from aristech.application.decision import Decision, decide
from aristech.application.health import FaultKind, HealthMonitor
from aristech.application.ports import HornetDetector, Notifier, VideoSource
from aristech.domain import Detection

_log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DetectHornetVisualConfig:
    """`confidence_threshold`: the ACT point for `decide()` (ADR-0004, ADR-0029).
    `count_threshold`: the COUNT point feeding the attack episodes (ADR-0014,
    ADR-0031); None means the ACT point. `COUNT <= ACT` must hold.
    `live_source`: a camera, whose end is a fault; a video file ends normally (ADR-0033)."""

    confidence_threshold: float = 0.5
    count_threshold: float | None = None
    episode_rule: EpisodeRule = field(default_factory=EpisodeRule)
    live_source: bool = False

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

    With a `HealthMonitor`, a heartbeat is sent when due, and a loop error or the end
    of a live source is sent as a rate-limited fault (ADR-0033).

    Every dependency is injected behind a port, so camera, model and notification
    channel can change without touching this use case.
    """

    def __init__(
        self,
        video: VideoSource,
        detector: HornetDetector,
        notifier: Notifier,
        config: DetectHornetVisualConfig | None = None,
        health: HealthMonitor | None = None,
    ) -> None:
        self._video = video
        self._detector = detector
        self._notifier = notifier
        self._config = config or DetectHornetVisualConfig()
        self._health = health

    def run(self) -> DetectionRun:
        """Consume the whole source, then close it, even on error. An episode still
        open when the run stops (end of stream, interruption or error) is closed at
        the last frame seen and its summary sent. An error is reported as a fault,
        then raised again."""
        threats = abstentions = episodes = frames = 0
        tracker = AttackEpisodeTracker(self._config.episode_rule)
        last_seen: datetime | None = None
        try:
            for frame in self._video.frames():
                hit = False
                for detection in self._detector.detect(frame):
                    decision = self._report(detection)
                    threats += decision is Decision.ACT
                    abstentions += decision is Decision.ABSTAIN
                    hit = hit or self._counts(detection)
                last_seen = frame.timestamp
                episodes += self._track(tracker.observe(frame.timestamp, hit))
                frames += 1
                self._beat(frames, episodes)
        except Exception as exc:
            self._fault(FaultKind.LOOP_ERROR, type(exc).__name__)
            raise
        finally:
            try:
                if last_seen is not None:
                    self._track(tracker.close(last_seen))
            finally:
                self._video.close()
        # Outside the try: a failing fault push must not be reported again as a loop error.
        if self._config.live_source:
            self._fault(FaultKind.SOURCE_ENDED, "the live source stopped sending frames")
        return DetectionRun(threats=threats, abstentions=abstentions, episodes=episodes)

    def _report(self, detection: Detection) -> Decision:
        """Apply the ACT / ABSTAIN / IGNORE rule and notify accordingly."""
        decision = decide(detection, self._config.confidence_threshold)
        if decision is Decision.ACT:
            self._notifier.notify_detection(detection)
        elif decision is Decision.ABSTAIN:
            self._notifier.notify_abstention(detection)
        else:
            _log.debug("ignore %s %.2f", detection.species.value, detection.confidence)
        return decision

    def _counts(self, detection: Detection) -> bool:
        """A *V. velutina* at or above the COUNT point makes its frame a hit."""
        return detection.is_threat() and detection.confidence >= self._config.count_point

    def _track(self, episode: AttackEpisode | None) -> int:
        """Notify an episode that opened (returns 1) or closed (returns 0)."""
        if episode is None:
            return 0
        if episode.ended is None:
            self._notifier.notify_attack_started(episode)
            return 1
        self._notifier.notify_attack_ended(episode)
        return 0

    def _beat(self, frames: int, episodes: int) -> None:
        """Send the heartbeat when the health monitor says one is due."""
        if self._health is not None and (beat := self._health.tick(frames, episodes)):
            self._notifier.notify_heartbeat(beat)

    def _fault(self, kind: FaultKind, detail: str) -> None:
        """Send a fault unless the rate limit mutes it."""
        if self._health is not None and (fault := self._health.fault(kind, detail)):
            self._notifier.notify_fault(fault)
