from collections.abc import Sequence
from typing import Protocol

from aristech.domain import Detection, VideoFrame


class HornetDetector(Protocol):
    def detect(self, frame: VideoFrame) -> Sequence[Detection]: ...
