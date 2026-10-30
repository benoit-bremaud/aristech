"""Capture-rig domain: rig states, segment metadata and the daylight window (spec capture-rig)."""

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from enum import Enum


class RigState(Enum):
    """Lifecycle of the rig (diagram capture-rig/04-state)."""

    IDLE = "idle"
    RECORDING = "recording"
    DEGRADED = "degraded"
    FAULT = "fault"


@dataclass(frozen=True, slots=True)
class SegmentMetadata:
    """Sidecar of one audio segment or video clip; enough to split a test set by day and hive."""

    rig_id: str
    hive_id: str
    site: str
    kind: str
    trigger: str
    start_utc: datetime
    end_utc: datetime
    clock_source: str
    software_version: str
    settings: Mapping[str, str | int | float] = field(default_factory=dict)
    missing_inputs: tuple[str, ...] = ()
    flagged: bool = False

    def to_dict(self) -> dict[str, object]:
        """JSON-ready mapping; timestamps as ISO 8601 UTC."""
        return {
            "rig_id": self.rig_id,
            "hive_id": self.hive_id,
            "site": self.site,
            "kind": self.kind,
            "trigger": self.trigger,
            "start_utc": self.start_utc.isoformat(),
            "end_utc": self.end_utc.isoformat(),
            "clock_source": self.clock_source,
            "software_version": self.software_version,
            "settings": dict(self.settings),
            "missing_inputs": list(self.missing_inputs),
            "flagged": self.flagged,
        }


_J2000 = 2451545.0
_UNIX_EPOCH_JD = 2440587.5
_SUN_ALTITUDE_DEG = -0.833  # refraction + solar disc radius


def daylight_window(
    day: date, latitude: float, longitude: float, margin: timedelta = timedelta(minutes=30)
) -> tuple[datetime, datetime]:
    """Return (sunrise − margin, sunset + margin) in UTC for `day` at the site.

    Sunrise equation (Meeus approximation, ~1 min accuracy at mid latitudes), so the rig needs
    no network. Polar day gives the whole UTC day, polar night an empty window (start == end).
    `longitude` is positive east. The window is computed for the UTC date `day`, which is the
    local date in Europe; far east of Greenwich the evening margin can fall on the next UTC day.
    """
    midnight = datetime(day.year, day.month, day.day, tzinfo=UTC)
    n = math.ceil(midnight.timestamp() / 86400 + _UNIX_EPOCH_JD - _J2000 + 0.0008)
    mean_noon = n - longitude / 360
    anomaly = math.radians((357.5291 + 0.98560028 * mean_noon) % 360)
    centre = 1.9148 * math.sin(anomaly) + 0.02 * math.sin(2 * anomaly)
    centre += 0.0003 * math.sin(3 * anomaly)
    ecliptic = math.radians((math.degrees(anomaly) + centre + 180 + 102.9372) % 360)
    transit = _J2000 + mean_noon + 0.0053 * math.sin(anomaly) - 0.0069 * math.sin(2 * ecliptic)
    declination = math.asin(math.sin(ecliptic) * math.sin(math.radians(23.4397)))
    lat = math.radians(latitude)
    cos_hour = (
        math.sin(math.radians(_SUN_ALTITUDE_DEG)) - math.sin(lat) * math.sin(declination)
    ) / (math.cos(lat) * math.cos(declination))
    if cos_hour <= -1:
        return midnight, midnight + timedelta(days=1)
    if cos_hour >= 1:
        return midnight, midnight
    half_day = math.degrees(math.acos(cos_hour)) / 360
    sunrise = _from_julian(transit - half_day)
    sunset = _from_julian(transit + half_day)
    return sunrise - margin, sunset + margin


def _from_julian(julian_day: float) -> datetime:
    return datetime.fromtimestamp((julian_day - _UNIX_EPOCH_JD) * 86400, tz=UTC)
