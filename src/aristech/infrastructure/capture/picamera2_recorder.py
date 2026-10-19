"""`CameraRecorder` over Picamera2: H.264 into a ring buffer, motion on the lores stream.

`CircularOutput2` delays every frame by `pre_roll_seconds`: opening an output writes the
buffered pre-roll, and frames reach the file only once they leave the buffer. Closing must
therefore wait `pre_roll_seconds` after the stop request, or the tail of the event is lost.
If a new clip starts during that wait, the old output is closed at once: the frames it had not
received yet are exactly the new clip's pre-roll.

Motion is checked by a background thread at `motion_hz` (mean absolute difference of the lores
luma plane above `motion_threshold`) and latched until `motion_detected()` reads it, so a short
visit between two one-second ticks is not missed. Picamera2 is imported lazily (extra
`capture`; on Raspberry Pi OS it comes from apt).
"""

import logging
import threading
from typing import Any

_log = logging.getLogger("aristech.capture")
_MAIN_SIZE = (1920, 1080)
_LORES_SIZE = (320, 240)


class Picamera2Recorder:
    """Camera Module 3 recorder (ADR-0017)."""

    def __init__(
        self,
        fps: int = 30,
        pre_roll_seconds: float = 5.0,
        motion_threshold: float = 8.0,
        motion_hz: float = 10.0,
    ) -> None:
        """Threshold is in luma levels (0–255)."""
        self._fps = fps
        self._pre_roll_seconds = pre_roll_seconds
        self._motion_threshold = motion_threshold
        self._motion_period = 1.0 / motion_hz
        self._camera: Any | None = None
        self._circular: Any | None = None
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
            circular = CircularOutput2(buffer_duration_ms=int(self._pre_roll_seconds * 1000))
            camera.start_recording(H264Encoder(), circular)
        except Exception:  # any camera error means "not healthy", retried
            _log.debug("camera unavailable", exc_info=True)
            return False
        self._camera, self._circular = camera, circular
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

    def start_clip(self, path: str) -> None:
        """Open an MP4 at `path` on the ring: buffered pre-roll first, then live frames."""
        if self._circular is None or self._clip_open:
            return
        self._close_pending_now()
        from picamera2.outputs import PyavOutput

        self._circular.open_output(PyavOutput(path))
        self._clip_open = True

    def stop_clip(self) -> None:
        """Close the clip once the ring has flushed the frames up to now."""
        if self._circular is None or not self._clip_open:
            self._clip_open = False
            return
        self._clip_open = False
        timer = threading.Timer(self._pre_roll_seconds, self._circular.close_output)
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
        self._clip_open = False
        if camera is not None:
            try:
                camera.stop_recording()
                camera.close()
            except Exception:  # releasing a dead camera; nothing else to do
                _log.debug("camera release failed", exc_info=True)
