from typing import Protocol

from aristech.domain import BoundingBox


class DistanceSensor(Protocol):
    """Mesure la distance vers une région d'intérêt (typiquement la bbox
    d'une détection). Retourne la distance en mètres, ou None si
    indisponible (hors champ ToF, occlusion stéréo, etc.)."""

    def distance_to(self, region: BoundingBox) -> float | None: ...
