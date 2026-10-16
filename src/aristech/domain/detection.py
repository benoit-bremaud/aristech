"""A single detector output."""

from dataclasses import dataclass
from datetime import datetime

from aristech.domain.geometry import BoundingBox
from aristech.domain.species import Species


@dataclass(frozen=True, slots=True)
class Detection:
    """One box reported by a detector, with a confidence in [0, 1]."""

    species: Species
    bbox: BoundingBox
    confidence: float
    timestamp: datetime

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {self.confidence}")

    def is_hornet(self) -> bool:
        """Any hornet, native *V. crabro* included; use `is_threat` to decide on action."""
        return self.species in (Species.VESPA_VELUTINA, Species.VESPA_CRABRO)

    def is_threat(self) -> bool:
        """Only the invasive *V. velutina*: the single species the system may act on.

        Kept in one place so the rule stays auditable; the native *V. crabro* is not a
        target (legal floor, ADR-0003).
        """
        return self.species is Species.VESPA_VELUTINA
