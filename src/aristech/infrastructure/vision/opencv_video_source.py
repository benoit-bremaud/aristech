"""`VideoSource` adapter backed by OpenCV (`cv2`).

Reads frames from a video file path or a camera index. `cv2` is imported
lazily so the core package installs and imports without the `vision` extra.

Frames are yielded with their pixels in OpenCV's native **BGR** order; the
detector adapter is responsible for any colour conversion it needs.
"""

from collections.abc import Iterator
from datetime import datetime, timezone
from typing import Any

from aristech.domain import VideoFrame


class OpenCVVideoSource:
    def __init__(self, source: str | int) -> None:
        """`source` is a video file path or an integer camera index."""
        self._source = source
        self._cap: Any | None = None

    def _capture(self) -> Any:
        if self._cap is None:
            import cv2

            cap = cv2.VideoCapture(self._source)
            if not cap.isOpened():
                raise RuntimeError(f"OpenCV could not open source: {self._source!r}")
            self._cap = cap
        return self._cap

    def frames(self) -> Iterator[VideoFrame]:
        cap = self._capture()
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            height, width = frame.shape[:2]
            yield VideoFrame(
                pixels=frame,
                width=int(width),
                height=int(height),
                timestamp=datetime.now(timezone.utc),
            )

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
