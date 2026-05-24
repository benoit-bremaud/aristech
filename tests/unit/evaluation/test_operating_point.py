from datetime import datetime

import pytest

from aristech.domain import BoundingBox, Detection, Species
from aristech.evaluation.metrics import Annotation, Sample, evaluate
from aristech.evaluation.operating_point import (
    bees_as_target_count,
    select_operating_point,
    threshold_sweep,
)

_BOX = BoundingBox(0, 0, 10, 10)


def _pred(species: Species, confidence: float) -> Detection:
    return Detection(
        species=species,
        bbox=_BOX,
        confidence=confidence,
        timestamp=datetime(2026, 5, 24),
    )


def _truth(species: Species) -> Annotation:
    return Annotation(species=species, bbox=_BOX)


def _samples_bee_misread_at_low_conf() -> list[Sample]:
    # Image A: a real bee, predicted as the target with low confidence 0.4 —
    # a dangerous false positive that a high-enough threshold filters out.
    # Image B: a real V. velutina predicted confidently (0.8).
    bee_image: Sample = (
        [_pred(Species.VESPA_VELUTINA, 0.4)],
        [_truth(Species.APIS_MELLIFERA)],
    )
    hornet_image: Sample = (
        [_pred(Species.VESPA_VELUTINA, 0.8)],
        [_truth(Species.VESPA_VELUTINA)],
    )
    return [bee_image, hornet_image]


def test_bees_as_target_count_reads_the_critical_cell() -> None:
    report = evaluate(_samples_bee_misread_at_low_conf(), confidence_threshold=0.3)
    assert bees_as_target_count(report) == 1
    # Above the bad prediction's confidence, the bee is no longer flagged.
    safe = evaluate(_samples_bee_misread_at_low_conf(), confidence_threshold=0.5)
    assert bees_as_target_count(safe) == 0


def test_threshold_sweep_tracks_bee_fp_and_recall() -> None:
    points = threshold_sweep(_samples_bee_misread_at_low_conf(), thresholds=[0.3, 0.5, 0.9])
    assert [p.confidence_threshold for p in points] == [0.3, 0.5, 0.9]
    by_t = {p.confidence_threshold: p for p in points}
    assert by_t[0.3].bees_as_target == 1  # unsafe: bee predicted as target
    assert by_t[0.5].bees_as_target == 0  # bad prediction dropped
    assert by_t[0.5].target.recall == 1.0  # real hornet still caught
    assert by_t[0.9].target.recall == 0.0  # hornet prediction (0.8) now dropped


def test_select_picks_lowest_safe_threshold_with_max_recall() -> None:
    chosen = select_operating_point(_samples_bee_misread_at_low_conf(), thresholds=[0.3, 0.5, 0.9])
    # 0.3 is unsafe (bee as target); 0.9 is safe but misses the hornet; 0.5 is
    # the safe threshold that still catches the hornet.
    assert chosen.confidence_threshold == 0.5
    assert chosen.bees_as_target == 0
    assert chosen.target.recall == 1.0


def test_select_raises_when_no_threshold_is_safe() -> None:
    # A bee misread as the target with very high confidence: no candidate
    # threshold can drive bees-as-target to zero.
    samples: list[Sample] = [
        ([_pred(Species.VESPA_VELUTINA, 0.99)], [_truth(Species.APIS_MELLIFERA)])
    ]
    with pytest.raises(ValueError, match="legal floor"):
        select_operating_point(samples, thresholds=[0.3, 0.5, 0.9])
