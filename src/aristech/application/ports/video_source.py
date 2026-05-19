from collections.abc import Iterator
from typing import Protocol

from aristech.domain import VideoFrame


class VideoSource(Protocol):
    def frames(self) -> Iterator[VideoFrame]: ...
    def close(self) -> None: ...
