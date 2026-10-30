from datetime import UTC, date, datetime, timedelta

import pytest

from aristech.domain import SegmentMetadata, daylight_window

_PARIS = (48.8566, 2.3522)


def _utc(*args: int) -> datetime:
    return datetime(*args, tzinfo=UTC)


def test_paris_equinox_sunrise_and_sunset_within_three_minutes() -> None:
    start, end = daylight_window(date(2026, 3, 20), *_PARIS, margin=timedelta(0))

    assert abs(start - _utc(2026, 3, 20, 5, 54)) < timedelta(minutes=3)
    assert abs(end - _utc(2026, 3, 20, 18, 3)) < timedelta(minutes=3)


def test_margin_widens_the_window_on_both_sides() -> None:
    bare = daylight_window(date(2026, 8, 15), *_PARIS, margin=timedelta(0))
    wide = daylight_window(date(2026, 8, 15), *_PARIS)

    assert wide == (bare[0] - timedelta(minutes=30), bare[1] + timedelta(minutes=30))


@pytest.mark.parametrize(
    ("day", "expected_hours"),
    [(date(2026, 6, 21), 24), (date(2026, 12, 21), 0)],
)
def test_polar_day_and_night(day: date, expected_hours: int) -> None:
    start, end = daylight_window(day, 78.0, 15.0)

    assert end - start == timedelta(hours=expected_hours)


def test_metadata_to_dict_is_json_ready() -> None:
    metadata = SegmentMetadata(
        rig_id="rig-1",
        hive_id="hive-a",
        site="home",
        kind="audio",
        trigger="continuous",
        start_utc=_utc(2026, 8, 1, 10),
        end_utc=_utc(2026, 8, 1, 10, 10),
        clock_source="ntp",
        software_version="abc123",
        settings={"sample_rate_hz": 48_000},
        missing_inputs=("colony",),
    )

    data = metadata.to_dict()

    assert data["start_utc"] == "2026-08-01T10:00:00+00:00"
    assert data["missing_inputs"] == ["colony"]
    assert data["settings"] == {"sample_rate_hz": 48_000}
    assert data["flagged"] is False
