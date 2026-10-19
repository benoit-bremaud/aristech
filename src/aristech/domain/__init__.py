"""Pure domain types: no I/O, stdlib only."""

from aristech.domain.capture import RigState, SegmentMetadata, daylight_window
from aristech.domain.detection import Detection
from aristech.domain.geometry import BoundingBox, Point2D
from aristech.domain.media import VideoFrame
from aristech.domain.species import Species

__all__ = [
    "BoundingBox",
    "Detection",
    "Point2D",
    "RigState",
    "SegmentMetadata",
    "Species",
    "VideoFrame",
    "daylight_window",
]
