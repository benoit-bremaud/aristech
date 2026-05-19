from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class VideoFrame:
    """Image capturée à un instant donné.

    `pixels` est un tableau opaque (typiquement numpy.ndarray) : le domain
    ne connaît pas numpy, mais accepte n'importe quel conteneur que les
    adaptateurs et use cases savent manipuler.
    """

    pixels: Any
    width: int
    height: int
    timestamp: datetime


@dataclass(frozen=True, slots=True)
class AudioSample:
    samples: Any
    sample_rate: int
    duration_s: float
    timestamp: datetime
