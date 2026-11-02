from datetime import datetime, timedelta

import pytest

from aristech.application.attack_episode import AttackEpisodeTracker, EpisodeRule

_T0 = datetime(2026, 11, 2, 12, 0, 0)
_RULE = EpisodeRule(min_hit_frames=3, window=timedelta(seconds=10), cooldown=timedelta(seconds=60))


def _at(seconds: float) -> datetime:
    return _T0 + timedelta(seconds=seconds)


def _feed(tracker: AttackEpisodeTracker, frames: list[tuple[float, bool]]) -> list:
    return [e for s, hit in frames if (e := tracker.observe(_at(s), hit)) is not None]


def test_episode_opens_once_on_the_nth_hit_within_the_window():
    events = _feed(AttackEpisodeTracker(_RULE), [(0, True), (1, True), (2, True), (3, True)])
    assert len(events) == 1
    assert events[0].started == _at(2) and events[0].ended is None
    assert events[0].hit_frames == 3


def test_hits_spread_wider_than_the_window_never_open():
    assert _feed(AttackEpisodeTracker(_RULE), [(0, True), (10, True), (20, True)]) == []


def test_single_alert_however_many_hits_in_the_episode():
    frames = [(float(s), True) for s in range(0, 120)]
    events = _feed(AttackEpisodeTracker(_RULE), frames)
    assert [e.ended for e in events] == [None]


def test_episode_closes_after_the_cooldown_with_its_summary():
    tracker = AttackEpisodeTracker(_RULE)
    frames = [(0, True), (1, True), (2, True), (3, True), (30, False), (62, False), (63, False)]
    events = _feed(tracker, frames)
    assert len(events) == 2
    ended = events[1]
    assert ended.started == _at(2) and ended.ended == _at(63)
    assert ended.peak == 4 and ended.hit_frames == 4


def test_pressure_back_before_the_cooldown_keeps_one_episode():
    frames = [(0, True), (1, True), (2, True), (40, True), (41, True), (42, True), (80, False)]
    events = _feed(AttackEpisodeTracker(_RULE), frames)
    assert [e.ended for e in events] == [None]


def test_a_new_episode_after_the_previous_closed_raises_a_new_alert():
    first = [(0, True), (1, True), (2, True), (70, False)]
    second = [(100, True), (101, True), (102, True)]
    events = _feed(AttackEpisodeTracker(_RULE), first + second)
    assert [e.ended is None for e in events] == [True, False, True]


def test_close_ends_an_open_episode_and_is_a_no_op_otherwise():
    tracker = AttackEpisodeTracker(_RULE)
    assert tracker.close(_at(0)) is None
    _feed(tracker, [(0, True), (1, True), (2, True)])
    ended = tracker.close(_at(5))
    assert ended is not None and ended.ended == _at(5)
    assert tracker.close(_at(6)) is None


@pytest.mark.parametrize(
    "kwargs",
    [
        {"min_hit_frames": 0},
        {"window": timedelta(0)},
        {"cooldown": timedelta(seconds=-1)},
    ],
)
def test_invalid_rule_is_rejected(kwargs):
    with pytest.raises(ValueError):
        EpisodeRule(**kwargs)
