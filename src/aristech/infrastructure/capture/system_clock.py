"""`Clock` over the system time, reporting whether NTP or the RTC backs it."""

import subprocess
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path


def _ntp_synchronized() -> bool:
    try:
        result = subprocess.run(
            ["timedatectl", "show", "-p", "NTPSynchronized", "--value"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.stdout.strip() == "yes"


class SystemClock:
    """UTC system time; `source()` is `ntp`, else `rtc` if a battery RTC exists, else `unsynced`."""

    def __init__(
        self,
        ntp_synchronized: Callable[[], bool] = _ntp_synchronized,
        rtc_device: Path = Path("/dev/rtc0"),
    ) -> None:
        """The NTP probe and RTC path are injectable for tests."""
        self._ntp_synchronized = ntp_synchronized
        self._rtc_device = rtc_device

    def now(self) -> datetime:
        """Current time, timezone-aware UTC."""
        return datetime.now(timezone.utc)

    def source(self) -> str:
        """Where the time comes from (spec A4)."""
        if self._ntp_synchronized():
            return "ntp"
        if self._rtc_device.exists():
            return "rtc"
        return "unsynced"
