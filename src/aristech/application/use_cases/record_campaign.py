"""Record a capture campaign (UC7, spec capture-rig): daylight audio, motion clips, rotation.

`tick()` is called about once a second by the composition root. Each tick is the self-check of
the state diagram: it re-reads free space, the daylight window and device health, then opens or
closes segments. Segment times come from the device where it knows better (audio sample
times, a clip's first-frame sensor time), otherwise from the `Clock`; all are UTC wall time. A
clip's file starts on a keyframe up to one GOP after the ring front, hence the camera's time
(#179); a time more than one GOP before the ring front or after the tick (wrong units or
origin) is rejected for the fallback, one ring before the tick.

A closed clip keeps receiving frames for one ring (the camera delays every frame by it), so its
sidecar is written only when the clip really ends: one ring after the close, or when the next
clip opens sooner (#178): the old file then ends at the ring front, one ring before the tick
(never after the new clip's start), and the frames up to the new clip's first keyframe (under
one GOP) are in neither file. `close()` releases the camera, which writes the ring into the
last clip first (#180), so there the clip ends at the release.
"""

import logging
from dataclasses import dataclass, field, replace
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
_GOP = timedelta(seconds=1)  # the camera adapter pins one keyframe a second


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
    # Budget between the first motion frame and the clip's first frame (#174, AC7): one tick
    # (1 s sleep + the tick's work) + the motion latch (0.1 s) + one GOP, since a clip starts on
    # a keyframe (1 s, the adapter pins it). The ring holds this margin on top of the pre-roll,
    # so 5 s hold while a tick's work stays under about 0.9 s. The opening tick then waits up to
    # one GOP for the clip's first frame (#179); the pre-roll is already fixed by then.
    pre_roll_margin: timedelta = timedelta(seconds=3)
    post_roll: timedelta = timedelta(seconds=5)
    max_clip: timedelta = timedelta(minutes=5)
    daylight_margin: timedelta = timedelta(minutes=30)
    rotate_below: float = 0.10
    stop_below: float = 0.02

    @property
    def ring(self) -> timedelta:
        """Length of the camera ring buffer: what a clip holds before the tick that opened it."""
        return self.pre_roll + self.pre_roll_margin


@dataclass(slots=True)
class _OpenSegment:
    path: str
    start: datetime
    trigger: str
    missing: set[str] = field(default_factory=set)


@dataclass(frozen=True, slots=True)
class _ClosingClip:
    segment: _OpenSegment
    closed_at: datetime
    settings: Settings


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
        self._closing: _ClosingClip | None = None
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
        space_ok = self._enough_space()  # rotation first, so a full disk can still recover
        if self._closing is not None and now - self._closing.closed_at >= self._config.ring:
            self._flush_closing(self._closing.closed_at)
        if not space_ok:
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
        now = self._clock.now()
        self._stop_all(now)
        self._camera.close()
        self._audio.close()
        if self._closing is not None:  # the release wrote the ring into it, up to now (#180)
            self._closing = replace(self._closing, closed_at=now)
        self._flush_closing(now)

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
                start = self._clip_start(now, self._camera.start_clip(path))
                self._clip = _OpenSegment(path, start, "motion", set(missing))
                # The old output closed when this one opened: its last frame was the ring front,
                # never after this clip's first frame (a latency-early start, #179).
                self._flush_closing(min(now - self._config.ring, start))
        clip = self._clip
        if clip is None or self._last_motion is None:
            return
        quiet = now - self._last_motion >= self._config.post_roll
        too_long = now - clip.start >= self._config.max_clip
        if quiet or too_long:
            self._close_clip(now)

    def _clip_start(self, now: datetime, first_frame: datetime | None) -> datetime:
        """The camera's first-frame time if it is plausible, else one ring before `now`."""
        ring_front = now - self._config.ring
        if first_frame is None:
            return ring_front
        # One GOP of slack below: the ring ages frames against the newest one, which arrives a
        # pipeline latency after its sensor time, so a correct time can predate `ring_front`.
        if not ring_front - _GOP <= first_frame <= now:
            _log.warning("clip first-frame time %s outside the ring, ignored", first_frame)
            return ring_front
        return first_frame

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
        self._closing = _ClosingClip(self._clip, now, self._camera.settings())
        self._clip = None

    def _flush_closing(self, ends_by: datetime) -> None:
        """Write the closing clip's sidecar, ending at its close or `ends_by`, the earlier."""
        closing = self._closing
        if closing is not None:
            end = min(closing.closed_at, ends_by)
            # Kept with its end on a write error, retried at the next tick.
            self._closing = _ClosingClip(closing.segment, end, closing.settings)
            self._write_sidecar(closing.segment, "video", end, closing.settings)
            self._closing = None

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
