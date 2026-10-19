"""`CameraRecorder` over Picamera2: H.264 into a RAM ring buffer, motion on the lores stream.

`CircularOutput2` keeps the last `ring_seconds` of encoded video; opening an output on it
writes that pre-roll first, then live frames. Motion = mean absolute difference of the lores
luma plane above `motion_threshold`. Picamera2 is imported lazily (extra `capture`; on
Raspberry Pi OS it comes from apt).
"""

import logging
from typing import Any

_log = logging.getLogger("aristech.capture")
_MAIN_SIZE = (1920, 1080)
_LORES_SIZE = (320, 240)


class Picamera2Recorder:
    """Camera Module 3 recorder (ADR-0017)."""

    def __init__(
        self, fps: int = 30, ring_seconds: float = 10.0, motion_threshold: float = 8.0
    ) -> None:
        """`ring_seconds` must cover the pre-roll; threshold is in luma levels (0–255)."""
        self._fps = fps
        self._ring_seconds = ring_seconds
        self._motion_threshold = motion_threshold
        self._camera: Any | None = None
        self._circular: Any | None = None
        self._previous: Any | None = None
        self._clip_open = False
        self._lost = False

    def healthy(self) -> bool:
        """Start the camera and the ring buffer on first call.

        After a mid-run loss it answers False once, so the use case closes the open clip, then
        retries. A camera that freezes without raising is not detected (known limit).
        """
        if self._lost:
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
                fps=self._fps,
            )
            camera.configure(config)
            circular = CircularOutput2(buffer_duration_ms=int(self._ring_seconds * 1000))
            camera.start_recording(H264Encoder(), circular)
        except Exception:  # noqa: BLE001 — any camera error means "not healthy", retried
            _log.debug("camera unavailable", exc_info=True)
            return False
        self._camera, self._circular = camera, circular
        return True

    def motion_detected(self) -> bool:
        """Compare the lores luma plane with the previous call's."""
        if self._camera is None:
            return False
        import numpy

        width, height = _LORES_SIZE
        try:
            luma = self._camera.capture_array("lores")[:height, :width].astype(numpy.int16)
        except Exception:  # noqa: BLE001 — a camera lost mid-run: release it, healthy() retries
            _log.warning("camera lost while capturing", exc_info=True)
            self.close()
            self._lost = True
            return False
        previous, self._previous = self._previous, luma
        if previous is None:
            return False
        return float(numpy.abs(luma - previous).mean()) > self._motion_threshold

    def start_clip(self, path: str) -> None:
        """Flush the ring buffer into an MP4 at `path` and keep writing."""
        if self._circular is None or self._clip_open:
            return
        from picamera2.outputs import PyavOutput

        self._circular.open_output(PyavOutput(path))
        self._clip_open = True

    def stop_clip(self) -> None:
        """Close the open clip."""
        if self._circular is not None and self._clip_open:
            self._circular.close_output()
        self._clip_open = False

    def settings(self) -> dict[str, str | int | float]:
        """Resolution, fps and the last exposure / gain metadata."""
        values: dict[str, str | int | float] = {
            "resolution": f"{_MAIN_SIZE[0]}x{_MAIN_SIZE[1]}",
            "fps": self._fps,
        }
        if self._camera is not None:
            try:
                metadata = self._camera.capture_metadata()
            except Exception:  # noqa: BLE001 — settings are best effort; the sidecar still goes out
                _log.debug("camera metadata unavailable", exc_info=True)
                return values
            for key in ("ExposureTime", "AnalogueGain", "Lux"):
                if key in metadata:
                    values[key] = metadata[key]
        return values

    def close(self) -> None:
        """Stop recording and release the camera."""
        self.stop_clip()
        if self._camera is not None:
            self._camera.stop_recording()
            self._camera.close()
            self._camera = None
            self._circular = None
