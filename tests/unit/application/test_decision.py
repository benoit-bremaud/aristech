from datetime import datetime

import pytest

from aristech.application.decision import Decision, decide
from aristech.domain import BoundingBox, Detection, Species


def _det(species: Species, confidence: float) -> Detection:
    return Detection(
        species=species,
        bbox=BoundingBox(0, 0, 10, 10),
        confidence=confidence,
        timestamp=datetime(2026, 5, 24),
    )


@pytest.mark.parametrize(
    "species,confidence,expected",
    [
        (Species.VESPA_VELUTINA, 0.9, Decision.ACT),
        (Species.VESPA_VELUTINA, 0.5, Decision.ACT),  # at threshold → act
        (Species.VESPA_VELUTINA, 0.49, Decision.ABSTAIN),  # just below → abstain
        (Species.VESPA_VELUTINA, 0.0, Decision.ABSTAIN),
        (Species.VESPA_CRABRO, 0.99, Decision.IGNORE),  # hornet, not the target
        (Species.APIS_MELLIFERA, 0.99, Decision.IGNORE),
        (Species.UNKNOWN, 0.99, Decision.IGNORE),
    ],
)
def test_decide(species: Species, confidence: float, expected: Decision) -> None:
    assert decide(_det(species, confidence), 0.5) is expected


@pytest.mark.parametrize("threshold", [0.0, 0.5, 1.0])
def test_bee_never_acts_regardless_of_threshold(threshold: float) -> None:
    # The legal floor: a honeybee must never trigger action, even at max
    # confidence and a zero threshold.
    assert decide(_det(Species.APIS_MELLIFERA, 1.0), threshold) is Decision.IGNORE


def test_uncertain_target_abstains_not_ignores() -> None:
    # Abstention is distinct from ignoring: a below-threshold target is an
    # uncertain threat the system declines to act on, not a non-threat.
    assert decide(_det(Species.VESPA_VELUTINA, 0.2), 0.5) is Decision.ABSTAIN
