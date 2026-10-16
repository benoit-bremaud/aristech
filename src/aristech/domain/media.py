"""Sensor data entering the domain."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class VideoFrame:
    """An image captured at a given instant.

    `pixels` is opaque (typically a `numpy.ndarray`): the domain does not know
    numpy, it carries whatever container the adapters and use cases handle.
    """

    pixels: Any
    width: int
    height: int
    timestamp: datetime
