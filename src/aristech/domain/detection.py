from dataclasses import dataclass
from datetime import datetime

from aristech.domain.geometry import BoundingBox
from aristech.domain.species import Species


@dataclass(frozen=True, slots=True)
class Detection:
    species: Species
    bbox: BoundingBox
    confidence: float
    timestamp: datetime

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {self.confidence}")

    def is_hornet(self) -> bool:
        return self.species in (Species.VESPA_VELUTINA, Species.VESPA_CRABRO)

    def is_threat(self) -> bool:
        return self.species is Species.VESPA_VELUTINA
