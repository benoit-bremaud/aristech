"""Record a capture campaign (UC7, spec capture-rig): daylight audio, motion clips, rotation.

`tick()` is called about once a second by the composition root. Each tick is the self-check of
the state diagram: it re-reads free space, the daylight window and device health, then opens or
closes segments. All timestamps come from one `Clock`.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from aristech.application.ports.capture import (
    AudioRecorder,
    CameraRecorder,
    Clock,
    SegmentStore,
    Settings,
)
from aristech.domain import RigState, SegmentMetadata, daylight_window

_log = logging.getLogger("aristech.capture")


@dataclass(frozen=True, slots=True)
class CampaignConfig:
    """Campaign identity and recording policy; defaults are the spec's."""

    rig_id: str
    hive_id: str
    site: str
    latitude: float
    longitude: float
    software_version: str = "unknown"
    audio_segment: timedelta = timedelta(minutes=10)
    pre_roll: timedelta = timedelta(seconds=5)
    post_roll: timedelta = timedelta(seconds=5)
    max_clip: timedelta = timedelta(minutes=5)
    daylight_margin: timedelta = timedelta(minutes=30)
    rotate_below: float = 0.10
    stop_below: float = 0.02


@dataclass(slots=True)
class _OpenSegment:
    path: str
    start: datetime
    trigger: str
    missing: set[str] = field(default_factory=set)


class RecordCampaign:
    """Drive the rig from its ports; holds the open segments and the rig state."""

    def __init__(
        self,
        config: CampaignConfig,
        clock: Clock,
        camera: CameraRecorder,
        audio: AudioRecorder,
        store: SegmentStore,
    ) -> None:
        """Wire the ports; nothing is opened before the first `tick()`."""
        self._config = config
        self._clock = clock
        self._camera = camera
        self._audio = audio
        self._store = store
        self._state = RigState.IDLE
        self._audio_segment: _OpenSegment | None = None
        self._clip: _OpenSegment | None = None
        self._last_motion: datetime | None = None

    @property
    def state(self) -> RigState:
        """The state reached at the last tick."""
        return self._state

    def tick(self) -> RigState:
        """Run one self-check and recording step; return the new state.

        Any adapter error (disk, device, encoder) moves the rig to FAULT and is retried at the
        next tick: an unattended rig must never stop on one failure.
        """
        now = self._clock.now()
        try:
            return self._tick(now)
        except Exception:  # noqa: BLE001 — see docstring; logged with the traceback
            _log.exception("recording step failed")
            self._abandon_segments()
            return self._enter(RigState.FAULT, "recording step failed")

    def _tick(self, now: datetime) -> RigState:
        if not self._enough_space():
            self._stop_all(now)
            return self._enter(RigState.FAULT, "free space below the stop threshold")
        start, end = daylight_window(
            now.date(), self._config.latitude, self._config.longitude, self._config.daylight_margin
        )
        if not start <= now < end:
            self._stop_all(now)
            return self._enter(RigState.IDLE, "outside the daylight window")
        camera_ok = self._camera.healthy()
        audio_ok = self._audio.healthy()
        if not camera_ok and not audio_ok:
            self._stop_all(now)
            return self._enter(RigState.FAULT, "all inputs lost")
        missing = self._missing_inputs(camera_ok, audio_ok)
        for segment in (self._audio_segment, self._clip):
            if segment is not None:
                segment.missing.update(missing)
        self._step_audio(now, audio_ok, missing)
        self._step_video(now, camera_ok, missing)
        if missing:
            return self._enter(RigState.DEGRADED, f"missing inputs: {', '.join(missing)}")
        return self._enter(RigState.RECORDING, "all inputs present")

    def close(self) -> None:
        """Close open segments and release the devices."""
        self._stop_all(self._clock.now())
        self._camera.close()
        self._audio.close()

    def _enough_space(self) -> bool:
        while self._store.free_fraction() < self._config.rotate_below:
            if not self._store.delete_oldest_unflagged():
                _log.warning("disk nearly full and nothing left to rotate")
                break
            _log.warning("disk nearly full: deleted the oldest non-flagged segment")
        return self._store.free_fraction() >= self._config.stop_below

    def _missing_inputs(self, camera_ok: bool, audio_ok: bool) -> tuple[str, ...]:
        missing: list[str] = []
        if not camera_ok:
            missing.append("camera")
        if audio_ok:
            missing.extend(self._audio.missing_channels())
        else:
            missing.append("audio")
        return tuple(missing)

    def _step_audio(self, now: datetime, audio_ok: bool, missing: tuple[str, ...]) -> None:
        segment = self._audio_segment
        if segment is not None and (
            not audio_ok or now - segment.start >= self._config.audio_segment
        ):
            self._close_audio(now)
            segment = None
        if segment is None and audio_ok:
            path = self._store.path_for("audio", now)
            self._audio.start_segment(path)
            self._audio_segment = _OpenSegment(path, now, "continuous", set(missing))

    def _step_video(self, now: datetime, camera_ok: bool, missing: tuple[str, ...]) -> None:
        if not camera_ok:
            self._close_clip(now)
            return
        if self._camera.motion_detected():
            self._last_motion = now
            if self._clip is None:
                path = self._store.path_for("video", now)
                self._camera.start_clip(path)
                start = now - self._config.pre_roll
                self._clip = _OpenSegment(path, start, "motion", set(missing))
        clip = self._clip
        if clip is None or self._last_motion is None:
            return
        quiet = now - self._last_motion >= self._config.post_roll
        too_long = now - clip.start >= self._config.max_clip
        if quiet or too_long:
            self._close_clip(now)

    def _stop_all(self, now: datetime) -> None:
        self._close_audio(now)
        self._close_clip(now)

    def _abandon_segments(self) -> None:
        """Best-effort release after a failed step; the next tick opens fresh segments."""
        for stop in (self._audio.stop_segment, self._camera.stop_clip):
            try:
                stop()
            except Exception:  # noqa: BLE001 — already in FAULT; keep releasing the others
                _log.debug("release after failure also failed", exc_info=True)
        self._audio_segment = None
        self._clip = None

    def _close_audio(self, now: datetime) -> None:
        if self._audio_segment is None:
            return
        span = self._audio.stop_segment()
        end = now
        if span is not None:
            self._audio_segment.start, end = span
        self._write_sidecar(self._audio_segment, "audio", end, self._audio.settings())
        self._audio_segment = None

    def _close_clip(self, now: datetime) -> None:
        if self._clip is None:
            return
        self._camera.stop_clip()
        self._write_sidecar(self._clip, "video", now, self._camera.settings())
        self._clip = None

    def _write_sidecar(
        self,
        segment: _OpenSegment,
        kind: str,
        end: datetime,
        settings: Settings,
    ) -> None:
        metadata = SegmentMetadata(
            rig_id=self._config.rig_id,
            hive_id=self._config.hive_id,
            site=self._config.site,
            kind=kind,
            trigger=segment.trigger,
            start_utc=segment.start,
            end_utc=end,
            clock_source=self._clock.source(),
            software_version=self._config.software_version,
            settings=dict(settings),
            missing_inputs=tuple(sorted(segment.missing)),
        )
        self._store.write_sidecar(segment.path, metadata)

    def _enter(self, state: RigState, reason: str) -> RigState:
        if state is not self._state:
            level = (
                logging.INFO if state in (RigState.IDLE, RigState.RECORDING) else logging.WARNING
            )
            _log.log(level, "rig %s -> %s (%s)", self._state.value, state.value, reason)
            self._state = state
        return state
