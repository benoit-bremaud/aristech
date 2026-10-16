"""Detector port."""

from collections.abc import Sequence
from typing import Protocol

from aristech.domain import Detection, VideoFrame


class HornetDetector(Protocol):
    """Turns a frame into detections; knows nothing about the decision rule."""

    def detect(self, frame: VideoFrame) -> Sequence[Detection]:
        """Every box above the detector's own floor, any species; may be empty."""
        ...
