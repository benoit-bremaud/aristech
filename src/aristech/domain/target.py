from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from aristech.domain.geometry import Point3D


@dataclass(frozen=True, slots=True)
class Target:
    id: UUID
    position: Point3D
    confidence: float
    last_seen: datetime

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {self.confidence}")

    @classmethod
    def new(cls, position: Point3D, confidence: float, now: datetime) -> "Target":
        return cls(id=uuid4(), position=position, confidence=confidence, last_seen=now)
