"""`CameraRecorder` over Picamera2: H.264 into a ring buffer, motion on the lores stream.

`CircularOutput2` delays every frame by `ring_seconds`: opening an output writes the
buffered frames (the pre-roll plus the margin for the tick that opened the clip, #174), and
frames reach the file only once they leave the buffer. Closing must therefore wait
`ring_seconds` after the stop request, or the tail of the event is lost.
If a new clip starts during that wait, the old output is closed at once: the frames it had not
received yet are exactly the new clip's pre-roll, and `RecordCampaign` dates its end there (#178).

`start_clip` returns the UTC time of the clip's first frame (#179): the ring writes from its first
keyframe old enough, then rebases timestamps to it, so the tap reads that keyframe's sensor time
(encoder origin + the ring's offset) when the first frame reaches the file, and maps it to UTC
against the boot clock (CLOCK_BOOTTIME per libcamera; equal to CLOCK_MONOTONIC on a Pi that
never suspends). The offset is a private attribute of
`CircularOutput2`: if it is missing the time is unknown and the use case falls back.

Motion is checked by a background thread at `motion_hz` (mean absolute difference of the lores
luma plane above `motion_threshold`) and latched until `motion_detected()` reads it, so a short
visit between two one-second ticks is not missed. Picamera2 is imported lazily (extra
`capture`; on Raspberry Pi OS it comes from apt).
"""

import logging
import threading
import time
from datetime import UTC, datetime, timedelta
from typing import Any

_log = logging.getLogger("aristech.capture")
_MAIN_SIZE = (1920, 1080)
_LORES_SIZE = (320, 240)
# After `open_output` the ring drops frames until a keyframe is one ring old: up to one GOP
# (1 s, iperiod = fps). Beyond one GOP and a few frames the start is reported unknown.
_FIRST_FRAME_TIMEOUT = 1.2


def _boot_to_utc(sensor_us: int) -> datetime:
    """Map a CLOCK_BOOTTIME time in microseconds to UTC against the current wall time."""
    age_us = time.clock_gettime_ns(time.CLOCK_BOOTTIME) // 1000 - sensor_us
    return datetime.now(UTC) - timedelta(microseconds=age_us)


class _FirstFrameTap:
    """Wrap a clip's output; on its first video frame, record that frame's sensor time in UTC."""

    def __init__(self, output: Any, encoder: Any, circular: Any) -> None:
        self._output = output
        self._encoder = encoder
        self._circular = circular
        self.first_frame: datetime | None = None
        self.written = threading.Event()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._output, name)

    def outputframe(
        self,
        frame: Any,
        keyframe: bool = True,
        timestamp: int | None = None,
        packet: Any = None,
        audio: bool = False,
    ) -> None:
        try:
            if not audio and not self.written.is_set():
                self._record_first_frame(timestamp or 0)
        finally:  # the file write never depends on the timing code
            self._output.outputframe(frame, keyframe, timestamp, packet, audio)

    def _record_first_frame(self, timestamp: int) -> None:
        try:
            origin = self._encoder.firsttimestamp + self._circular._time_offset
            self.first_frame = _boot_to_utc(int(origin) + timestamp)
        except (AttributeError, TypeError):  # picamera2 internals changed: start unknown
            _log.warning("clip first-frame time unavailable", exc_info=True)
        finally:
            self.written.set()


class Picamera2Recorder:
    """Camera Module 3 recorder (ADR-0017)."""

    def __init__(
        self,
        fps: int = 30,
        ring_seconds: float = 8.0,
        motion_threshold: float = 8.0,
        motion_hz: float = 10.0,
    ) -> None:
        """Threshold is in luma levels (0–255); `ring_seconds` is `CampaignConfig.ring`."""
        self._fps = fps
        self._ring_seconds = ring_seconds
        self._motion_threshold = motion_threshold
        self._motion_period = 1.0 / motion_hz
        self._camera: Any | None = None
        self._circular: Any | None = None
        self._encoder: Any | None = None
        self._clip_open = False
        self._pending_close: threading.Timer | None = None
        self._lock = threading.Lock()
        self._motion = False
        self._lost = False
        self._stop = threading.Event()
        self._watcher: threading.Thread | None = None

    def healthy(self) -> bool:
        """Start the camera, the ring buffer and the motion thread on first call.

        After a mid-run loss it answers False once, so the use case closes the open clip, then
        retries. A camera that freezes without raising is not detected (known limit).
        """
        if self._lost:
            self._release()
            self._lost = False
            return False
        if self._camera is not None:
            return True
        try:
            from picamera2 import Picamera2
            from picamera2.encoders import H264Encoder
            from picamera2.outputs import CircularOutput2

            camera = Picamera2()
            config = camera.create_video_configuration(
                main={"size": _MAIN_SIZE},
                lores={"size": _LORES_SIZE, "format": "YUV420"},
                controls={"FrameRate": self._fps},
            )
            camera.configure(config)
            circular = CircularOutput2(buffer_duration_ms=int(self._ring_seconds * 1000))
            # One keyframe a second: a clip starts on a keyframe, so this bounds the pre-roll lost
            # to GOP alignment (CampaignConfig.pre_roll_margin).
            encoder = H264Encoder(iperiod=self._fps)
            camera.start_recording(encoder, circular)
        except Exception:  # any camera error means "not healthy", retried
            _log.debug("camera unavailable", exc_info=True)
            return False
        self._camera, self._circular, self._encoder = camera, circular, encoder
        self._stop.clear()
        self._watcher = threading.Thread(target=self._watch, args=(camera,), daemon=True)
        self._watcher.start()
        return True

    def _watch(self, camera: Any) -> None:
        previous: Any | None = None
        while not self._stop.is_set():
            try:
                luma = self._luma(camera)
            except Exception:  # a camera lost mid-run: flag it, healthy() reports
                _log.warning("camera lost while capturing", exc_info=True)
                self._lost = True
                return
            if previous is not None and self._changed(previous, luma):
                with self._lock:
                    self._motion = True
            previous = luma
            self._stop.wait(self._motion_period)

    @staticmethod
    def _luma(camera: Any) -> Any:
        import numpy

        width, height = _LORES_SIZE
        return camera.capture_array("lores")[:height, :width].astype(numpy.int16)

    def _changed(self, previous: Any, luma: Any) -> bool:
        import numpy

        return float(numpy.abs(luma - previous).mean()) > self._motion_threshold

    def motion_detected(self) -> bool:
        """True if motion was seen since the last call."""
        with self._lock:
            motion, self._motion = self._motion, False
        return motion

    def start_clip(self, path: str) -> datetime | None:
        """Open an MP4 at `path` on the ring; return the UTC time of its first frame.

        The buffered pre-roll goes first, then live frames. None if no clip was opened or the
        first frame did not arrive within `_FIRST_FRAME_TIMEOUT`.
        """
        if self._circular is None or self._clip_open:
            return None
        self._close_pending_now()
        from picamera2.outputs import PyavOutput

        tap = _FirstFrameTap(PyavOutput(path), self._encoder, self._circular)
        self._circular.open_output(tap)
        self._clip_open = True
        tap.written.wait(_FIRST_FRAME_TIMEOUT)
        return tap.first_frame

    def stop_clip(self) -> None:
        """Close the clip once the ring has flushed the frames up to now."""
        if self._circular is None or not self._clip_open:
            self._clip_open = False
            return
        self._clip_open = False
        timer = threading.Timer(self._ring_seconds, self._circular.close_output)
        timer.daemon = True
        self._pending_close = timer
        timer.start()

    def _close_pending_now(self) -> None:
        timer, self._pending_close = self._pending_close, None
        if timer is not None and timer.is_alive():
            timer.cancel()
            if self._circular is not None:
                self._circular.close_output()

    def settings(self) -> dict[str, str | int | float]:
        """Resolution, fps and the last exposure / gain metadata."""
        values: dict[str, str | int | float] = {
            "resolution": f"{_MAIN_SIZE[0]}x{_MAIN_SIZE[1]}",
            "fps": self._fps,
        }
        if self._camera is not None:
            try:
                metadata = self._camera.capture_metadata()
            except Exception:  # settings are best effort; the sidecar still goes out
                _log.debug("camera metadata unavailable", exc_info=True)
                return values
            for key in ("ExposureTime", "AnalogueGain", "Lux"):
                if key in metadata:
                    values[key] = metadata[key]
        return values

    def close(self) -> None:
        """Flush the last clip, stop recording and release the camera."""
        if self._clip_open and self._circular is not None:
            self._circular.close_output()
            self._clip_open = False
        self._close_pending_now()
        self._release()

    def _release(self) -> None:
        self._stop.set()
        watcher, self._watcher = self._watcher, None
        if watcher is not None and watcher is not threading.current_thread():
            watcher.join(timeout=2)
        camera, self._camera = self._camera, None
        self._circular = None
        self._encoder = None
        self._clip_open = False
        if camera is not None:
            try:
                camera.stop_recording()
                camera.close()
            except Exception:  # releasing a dead camera; nothing else to do
                _log.debug("camera release failed", exc_info=True)
