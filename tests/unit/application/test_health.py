"""Health rule (ADR-0033) with a hand-written fake clock."""

from datetime import UTC, datetime, timedelta

import pytest

from aristech.application.health import FaultKind, HealthMonitor, HealthRule

T0 = datetime(2026, 11, 2, 8, tzinfo=UTC)


class FakeClock:
    def __init__(self) -> None:
        self.at = T0

    def now(self) -> datetime:
        return self.at

    def source(self) -> str:
        return "ntp"

    def advance(self, **delta: float) -> None:
        self.at += timedelta(**delta)


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


def _monitor(clock: FakeClock) -> HealthMonitor:
    return HealthMonitor(HealthRule(timedelta(hours=24), timedelta(hours=1)), clock)


def test_heartbeat_is_due_at_the_period_not_before(clock):
    monitor = _monitor(clock)
    clock.advance(hours=23, minutes=59)
    assert monitor.tick(frames=10, episodes=0) is None
    clock.advance(minutes=1)
    beat = monitor.tick(frames=11, episodes=2)
    assert beat is not None
    assert (beat.at, beat.up_since, beat.frames, beat.episodes) == (clock.at, T0, 11, 2)


def test_next_heartbeat_waits_a_full_period(clock):
    monitor = _monitor(clock)
    clock.advance(hours=25)
    assert monitor.tick(1, 0) is not None
    clock.advance(hours=23)
    assert monitor.tick(2, 0) is None
    clock.advance(hours=1)
    assert monitor.tick(3, 0) is not None


def test_same_fault_is_muted_in_the_cooldown_and_counted(clock):
    monitor = _monitor(clock)
    first = monitor.fault(FaultKind.LOOP_ERROR, "OSError")
    assert first is not None
    assert first.suppressed == 0
    clock.advance(minutes=30)
    assert monitor.fault(FaultKind.LOOP_ERROR, "OSError") is None
    assert monitor.fault(FaultKind.LOOP_ERROR, "OSError") is None
    clock.advance(minutes=30)
    again = monitor.fault(FaultKind.LOOP_ERROR, "OSError")
    assert again is not None
    assert again.suppressed == 2
    assert again.at == clock.at


def test_another_fault_kind_is_not_muted(clock):
    monitor = _monitor(clock)
    assert monitor.fault(FaultKind.LOOP_ERROR, "x") is not None
    assert monitor.fault(FaultKind.SOURCE_ENDED, "y") is not None


@pytest.mark.parametrize(("heartbeat", "cooldown"), [(0, 1), (1, 0), (-1, 1)])
def test_rule_rejects_non_positive_durations(heartbeat, cooldown):
    period, quiet = timedelta(seconds=heartbeat), timedelta(seconds=cooldown)
    with pytest.raises(ValueError, match="positive"):
        HealthRule(period, quiet)
