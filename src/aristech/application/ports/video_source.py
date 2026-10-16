"""Video input port."""

from collections.abc import Iterator
from typing import Protocol

from aristech.domain import VideoFrame


class VideoSource(Protocol):
    """A stream of frames from a file or a camera."""

    def frames(self) -> Iterator[VideoFrame]:
        """Yield frames until the source ends; a live camera may never end."""
        ...

    def close(self) -> None:
        """Release the device or file; safe to call more than once."""
        ...
