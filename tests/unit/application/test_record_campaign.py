from collections.abc import Mapping
from datetime import datetime, timedelta, timezone

import pytest

from aristech.application.use_cases import CampaignConfig, RecordCampaign
from aristech.domain import RigState, SegmentMetadata

_NOON = datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc)
_MIDNIGHT = datetime(2026, 8, 15, 0, 0, tzinfo=timezone.utc)


class _FakeClock:
    def __init__(self, now: datetime) -> None:
        self.current = now
        self.clock_source = "ntp"

    def now(self) -> datetime:
        return self.current

    def source(self) -> str:
        return self.clock_source

    def advance(self, seconds: float) -> None:
        self.current += timedelta(seconds=seconds)


class _FakeCamera:
    def __init__(self) -> None:
        self.ok = True
        self.motion = False
        self.clips: list[str] = []
        self.open_clip: str | None = None
        self.closed = False

    def healthy(self) -> bool:
        return self.ok

    def motion_detected(self) -> bool:
        return self.motion

    def start_clip(self, path: str) -> None:
        self.clips.append(path)
        self.open_clip = path

    def stop_clip(self) -> None:
        self.open_clip = None

    def settings(self) -> Mapping[str, str | int | float]:
        return {"fps": 30}

    def close(self) -> None:
        self.closed = True


class _FakeAudio:
    def __init__(self) -> None:
        self.ok = True
        self.missing: tuple[str, ...] = ()
        self.segments: list[str] = []
        self.open_segment: str | None = None
        self.closed = False
        self.span: tuple[datetime, datetime] | None = None

    def healthy(self) -> bool:
        return self.ok

    def missing_channels(self) -> tuple[str, ...]:
        return self.missing

    def start_segment(self, path: str) -> None:
        self.segments.append(path)
        self.open_segment = path

    def stop_segment(self) -> tuple[datetime, datetime] | None:
        self.open_segment = None
        return self.span

    def settings(self) -> Mapping[str, str | int | float]:
        return {"sample_rate_hz": 48_000}

    def close(self) -> None:
        self.closed = True


class _FakeStore:
    def __init__(self) -> None:
        self.free = 0.5
        self.sidecars: dict[str, SegmentMetadata] = {}
        self.deletable = 0
        self.deleted = 0
        self._count = 0

    def path_for(self, kind: str, start: datetime) -> str:
        self._count += 1
        return f"{kind}-{self._count}"

    def write_sidecar(self, path: str, metadata: SegmentMetadata) -> None:
        self.sidecars[path] = metadata

    def free_fraction(self) -> float:
        return self.free

    def delete_oldest_unflagged(self) -> bool:
        if self.deletable == 0:
            return False
        self.deletable -= 1
        self.deleted += 1
        self.free += 0.05
        return True


class _Rig:
    def __init__(self, now: datetime = _NOON) -> None:
        self.clock = _FakeClock(now)
        self.camera = _FakeCamera()
        self.audio = _FakeAudio()
        self.store = _FakeStore()
        config = CampaignConfig(
            rig_id="rig-1", hive_id="hive-a", site="home", latitude=48.85, longitude=2.35
        )
        self.campaign = RecordCampaign(config, self.clock, self.camera, self.audio, self.store)

    def run(self, seconds: int) -> None:
        for _ in range(seconds):
            self.campaign.tick()
            self.clock.advance(1)


def test_daylight_records_audio_continuously_and_no_clip_without_motion() -> None:
    rig = _Rig()

    assert rig.campaign.tick() is RigState.RECORDING
    assert rig.audio.open_segment == "audio-1"
    assert rig.camera.clips == []


def test_audio_segments_rotate_every_ten_minutes_with_sidecar() -> None:
    rig = _Rig()

    rig.run(601)

    assert rig.audio.segments == ["audio-1", "audio-2"]
    sidecar = rig.store.sidecars["audio-1"]
    assert sidecar.end_utc - sidecar.start_utc == timedelta(minutes=10)
    assert (sidecar.hive_id, sidecar.kind, sidecar.trigger) == ("hive-a", "audio", "continuous")
    assert sidecar.clock_source == "ntp"


def test_motion_clip_has_pre_roll_and_closes_after_post_roll() -> None:
    rig = _Rig()
    rig.camera.motion = True
    rig.run(3)
    rig.camera.motion = False

    rig.run(6)

    assert rig.camera.clips == ["video-2"]
    assert rig.camera.open_clip is None
    sidecar = rig.store.sidecars["video-2"]
    assert sidecar.start_utc == _NOON - timedelta(seconds=5)
    assert sidecar.end_utc == _NOON + timedelta(seconds=7)
    assert sidecar.trigger == "motion"


def test_continuous_motion_is_capped_at_five_minutes() -> None:
    rig = _Rig()
    rig.camera.motion = True

    rig.run(300)

    assert len(rig.camera.clips) == 2


def test_outside_daylight_is_idle_and_closes_open_segments() -> None:
    rig = _Rig(now=_MIDNIGHT)

    assert rig.campaign.tick() is RigState.IDLE
    assert rig.audio.segments == []


def test_window_close_ends_recording() -> None:
    rig = _Rig()
    rig.campaign.tick()
    rig.clock.current = _NOON.replace(hour=23)

    assert rig.campaign.tick() is RigState.IDLE
    assert rig.audio.open_segment is None
    assert "audio-1" in rig.store.sidecars


def test_lost_microphone_degrades_and_video_goes_on() -> None:
    rig = _Rig()
    rig.campaign.tick()
    rig.audio.ok = False
    rig.camera.motion = True

    assert rig.campaign.tick() is RigState.DEGRADED
    assert rig.audio.open_segment is None
    assert rig.store.sidecars["audio-1"].missing_inputs == ("audio",)
    assert rig.camera.open_clip is not None


def test_silent_channel_is_degraded_and_recorded_in_sidecars() -> None:
    rig = _Rig()
    rig.audio.missing = ("colony",)
    rig.campaign.tick()
    rig.campaign.close()

    assert rig.campaign.state is RigState.DEGRADED
    assert rig.store.sidecars["audio-1"].missing_inputs == ("colony",)


def test_lost_camera_degrades_and_audio_goes_on() -> None:
    rig = _Rig()
    rig.camera.ok = False

    assert rig.campaign.tick() is RigState.DEGRADED
    assert rig.audio.open_segment == "audio-1"


def test_all_inputs_lost_is_fault_then_recovers() -> None:
    rig = _Rig()
    rig.camera.ok = rig.audio.ok = False
    assert rig.campaign.tick() is RigState.FAULT

    rig.camera.ok = rig.audio.ok = True

    assert rig.campaign.tick() is RigState.RECORDING


def test_low_disk_rotates_oldest_segments_without_motion() -> None:
    rig = _Rig()
    rig.store.free = 0.05
    rig.store.deletable = 3

    assert rig.campaign.tick() is RigState.RECORDING
    assert rig.store.deleted == 1


def test_disk_full_with_nothing_to_rotate_is_fault() -> None:
    rig = _Rig()
    rig.campaign.tick()
    rig.store.free = 0.01

    assert rig.campaign.tick() is RigState.FAULT
    assert rig.audio.open_segment is None


def test_close_releases_devices_and_closes_segments() -> None:
    rig = _Rig()
    rig.campaign.tick()

    rig.campaign.close()

    assert rig.camera.closed and rig.audio.closed
    assert "audio-1" in rig.store.sidecars


def test_unsynced_clock_is_written_in_sidecars() -> None:
    rig = _Rig()
    rig.clock.clock_source = "unsynced"
    rig.campaign.tick()
    rig.campaign.close()

    assert rig.store.sidecars["audio-1"].clock_source == "unsynced"


@pytest.mark.parametrize("module", ["aristech.domain", "aristech.application"])
def test_core_layers_never_import_capture_libraries(module: str) -> None:
    import importlib
    import sys

    for name in ("picamera2", "sounddevice", "soundfile"):
        sys.modules.pop(name, None)
    importlib.import_module(module)
    importlib.import_module("aristech.application.use_cases.record_campaign")

    assert not {"picamera2", "sounddevice", "soundfile"} & set(sys.modules)


def test_adapter_error_is_fault_and_next_tick_retries() -> None:
    rig = _Rig()

    def broken(path: str) -> None:
        raise OSError("disk I/O error")

    rig.audio.start_segment = broken  # type: ignore[method-assign]
    assert rig.campaign.tick() is RigState.FAULT

    del rig.audio.start_segment
    assert rig.campaign.tick() is RigState.RECORDING


def test_input_lost_mid_segment_is_kept_in_the_sidecar() -> None:
    rig = _Rig()
    rig.campaign.tick()
    rig.audio.missing = ("colony",)
    rig.campaign.tick()
    rig.audio.missing = ()
    rig.campaign.tick()

    rig.campaign.close()

    assert rig.store.sidecars["audio-1"].missing_inputs == ("colony",)


def test_audio_segment_is_dated_from_the_samples_written() -> None:
    rig = _Rig()
    rig.campaign.tick()
    rig.clock.advance(20)
    first = _NOON + timedelta(seconds=0.5)
    last = _NOON + timedelta(seconds=20.1)
    rig.audio.span = (first, last)

    rig.campaign.close()

    sidecar = rig.store.sidecars["audio-1"]
    assert (sidecar.start_utc, sidecar.end_utc) == (first, last)
