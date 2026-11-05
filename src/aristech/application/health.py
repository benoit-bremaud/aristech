"""Unit health: periodic heartbeat and rate-limited faults (ADR-0006, ADR-0033)."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # the Notifier port imports this module: no runtime cycle
    from aristech.application.ports import Clock


class FaultKind(Enum):
    """Faults the unit can detect and still deliver (ADR-0033)."""

    LOOP_ERROR = "loop_error"
    SOURCE_ENDED = "source_ended"


@dataclass(frozen=True, slots=True)
class HealthRule:
    """`heartbeat`: period of the alive message; `fault_cooldown`: at most one push per
    fault kind within it. Defaults from ADR-0033, overridable in the config."""

    heartbeat: timedelta = timedelta(hours=24)
    fault_cooldown: timedelta = timedelta(hours=1)

    def __post_init__(self) -> None:
        if self.heartbeat <= timedelta(0) or self.fault_cooldown <= timedelta(0):
            raise ValueError("heartbeat and fault_cooldown must be positive")


@dataclass(frozen=True, slots=True)
class Heartbeat:
    """The unit is alive: uptime and the work done since it started."""

    at: datetime
    up_since: datetime
    frames: int
    episodes: int


@dataclass(frozen=True, slots=True)
class Fault:
    """A detected fault; `suppressed` counts the same-kind faults muted since the last push."""

    kind: FaultKind
    at: datetime
    detail: str
    suppressed: int = 0


class HealthMonitor:
    """Decides when a heartbeat is due and which faults get through the rate limit.

    Time comes from an injected `Clock` (wall clock, never the video time), so the rule
    is pure and tested with a fake clock.
    """

    def __init__(self, rule: HealthRule, clock: "Clock") -> None:
        self._rule = rule
        self._clock = clock
        self._up_since = clock.now()
        self._next_heartbeat = self._up_since + rule.heartbeat
        self._last_fault: dict[FaultKind, datetime] = {}
        self._suppressed: dict[FaultKind, int] = {}

    def tick(self, frames: int, episodes: int) -> Heartbeat | None:
        """Return a heartbeat when one is due, else None; called once per frame, so a
        source that hangs sends no heartbeat, which is the signal (ADR-0033)."""
        now = self._clock.now()
        if now < self._next_heartbeat:
            return None
        self._next_heartbeat = now + self._rule.heartbeat
        return Heartbeat(at=now, up_since=self._up_since, frames=frames, episodes=episodes)

    def fault(self, kind: FaultKind, detail: str) -> Fault | None:
        """Return the fault to push, or None when the same kind was pushed within the
        cool-down; muted faults are counted and reported with the next push."""
        now = self._clock.now()
        last = self._last_fault.get(kind)
        if last is not None and now - last < self._rule.fault_cooldown:
            self._suppressed[kind] = self._suppressed.get(kind, 0) + 1
            return None
        self._last_fault[kind] = now
        return Fault(kind=kind, at=now, detail=detail, suppressed=self._suppressed.pop(kind, 0))
