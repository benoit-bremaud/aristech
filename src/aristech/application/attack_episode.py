"""Attack episode rule: one alert per episode, never one per frame (ADR-0031)."""

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True, slots=True)
class EpisodeRule:
    """`min_hit_frames` frames with a counted *V. velutina* within `window` open an
    episode; `cooldown` without that pressure closes it. Provisional values, to be
    set from field data (spec attack-alert, AC3)."""

    min_hit_frames: int = 3
    window: timedelta = timedelta(seconds=10)
    cooldown: timedelta = timedelta(seconds=60)

    def __post_init__(self) -> None:
        if self.min_hit_frames < 1:
            raise ValueError("min_hit_frames must be >= 1")
        if self.window <= timedelta(0) or self.cooldown <= timedelta(0):
            raise ValueError("window and cooldown must be positive")


@dataclass(frozen=True, slots=True)
class AttackEpisode:
    """An attack episode: `ended` is None while it lasts; `peak` is the highest
    hit-frame count seen in one window; `hit_frames` the total while it lasted."""

    started: datetime
    hit_frames: int
    peak: int
    ended: datetime | None = None


class AttackEpisodeTracker:
    """Feeds on one observation per frame and reports when an episode opens or closes.

    Time comes from the frame timestamps, so the rule is pure and tested with
    scripted timestamps, no clock.
    """

    def __init__(self, rule: EpisodeRule | None = None) -> None:
        self._rule = rule or EpisodeRule()
        self._hits: deque[datetime] = deque()
        self._open: AttackEpisode | None = None
        self._last_pressure: datetime | None = None

    def observe(self, timestamp: datetime, hit: bool) -> AttackEpisode | None:
        """Record a frame; return the episode when it opens (`ended` None) or closes."""
        if hit:
            self._hits.append(timestamp)
        while self._hits and timestamp - self._hits[0] >= self._rule.window:
            self._hits.popleft()
        pressure = len(self._hits) >= self._rule.min_hit_frames
        episode = self._open
        if episode is None:
            if not pressure:
                return None
            self._open = AttackEpisode(
                started=timestamp, hit_frames=len(self._hits), peak=len(self._hits)
            )
            self._last_pressure = timestamp
            return self._open
        self._open = episode = AttackEpisode(
            started=episode.started,
            hit_frames=episode.hit_frames + hit,
            peak=max(episode.peak, len(self._hits)),
        )
        if pressure:
            self._last_pressure = timestamp
            return None
        if (
            self._last_pressure is not None
            and timestamp - self._last_pressure >= self._rule.cooldown
        ):
            return self.close(timestamp)
        return None

    def close(self, timestamp: datetime) -> AttackEpisode | None:
        """Close the open episode at `timestamp` (end of stream); None if none is open."""
        episode = self._open
        if episode is None:
            return None
        self._open = None
        self._hits.clear()
        return AttackEpisode(episode.started, episode.hit_frames, episode.peak, ended=timestamp)
