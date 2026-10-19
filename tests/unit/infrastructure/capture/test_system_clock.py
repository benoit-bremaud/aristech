from pathlib import Path

from aristech.infrastructure.capture import SystemClock


def test_now_is_utc() -> None:
    assert SystemClock(lambda: True).now().utcoffset() is not None


def test_source_prefers_ntp(tmp_path: Path) -> None:
    assert SystemClock(lambda: True, tmp_path).source() == "ntp"


def test_source_falls_back_to_rtc(tmp_path: Path) -> None:
    assert SystemClock(lambda: False, tmp_path).source() == "rtc"


def test_source_unsynced_without_ntp_or_rtc(tmp_path: Path) -> None:
    assert SystemClock(lambda: False, tmp_path / "missing").source() == "unsynced"
