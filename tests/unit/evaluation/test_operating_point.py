from datetime import datetime

import pytest

from aristech.domain import BoundingBox, Detection, Species
from aristech.evaluation.metrics import Annotation, Sample, evaluate
from aristech.evaluation.operating_point import (
    bees_as_target_count,
    false_alert_rate,
    image_point,
    rule_of_three_bound,
    select_count_point,
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


_HORNET_IMAGE: Sample = (
    [_pred(Species.VESPA_VELUTINA, 0.8)],
    [_truth(Species.VESPA_VELUTINA)],
)
_BEE_MISREAD_IMAGE: Sample = (
    [_pred(Species.VESPA_VELUTINA, 0.4)],
    [_truth(Species.APIS_MELLIFERA)],
)


@pytest.mark.parametrize(
    ("samples", "expected_threshold"),
    [
        ([_HORNET_IMAGE], 0.1),
        ([_BEE_MISREAD_IMAGE, _HORNET_IMAGE], 0.5),
        ([_BEE_MISREAD_IMAGE], 0.5),
        ([], 0.1),
    ],
    ids=["hornet-only", "bee-misread-and-hornet", "bee-misread-only", "empty"],
)
def test_selected_operating_point_never_flags_a_bee(
    samples: list[Sample], expected_threshold: float
) -> None:
    point = select_operating_point(samples, thresholds=[0.1, 0.3, 0.5, 0.9])
    assert point.bees_as_target == 0
    # Independent of the selector's own filter: the bee read at 0.4 must be cut.
    assert point.confidence_threshold == expected_threshold
    assert bees_as_target_count(evaluate(samples, confidence_threshold=expected_threshold)) == 0


@pytest.mark.parametrize(
    ("trials", "bound"),
    [(0, 1.0), (1, 1.0), (3, 1.0), (300, 0.01), (780, 3 / 780)],
)
def test_rule_of_three_bound(trials: int, bound: float) -> None:
    assert rule_of_three_bound(trials) == pytest.approx(bound)


def test_select_records_bee_count_and_bound() -> None:
    chosen = select_operating_point(_samples_bee_misread_at_low_conf(), thresholds=[0.3, 0.5, 0.9])
    assert chosen.bee_count == 1
    assert chosen.bees_as_target_bound == 1.0


def test_margin_skips_the_first_safe_threshold() -> None:
    # 0.3 unsafe, 0.5 first safe: with one step of margin, 0.5 is too close to
    # the bee read at 0.4, so 0.7 is chosen (still catches the 0.8 hornet).
    chosen = select_operating_point(
        _samples_bee_misread_at_low_conf(), thresholds=[0.3, 0.5, 0.7, 0.9], margin_steps=1
    )
    assert chosen.confidence_threshold == 0.7
    assert chosen.target.recall == 1.0


def test_margin_never_picks_the_first_candidate() -> None:
    # Nothing below the first candidate witnesses that it is safe.
    chosen = select_operating_point([_HORNET_IMAGE], thresholds=[0.1, 0.3], margin_steps=1)
    assert chosen.confidence_threshold == 0.3


def test_margin_raises_when_no_threshold_has_room() -> None:
    samples = _samples_bee_misread_at_low_conf()
    with pytest.raises(ValueError, match="legal floor"):
        select_operating_point(samples, thresholds=[0.3, 0.5], margin_steps=2)


def test_negative_margin_is_rejected() -> None:
    with pytest.raises(ValueError, match="margin_steps"):
        select_operating_point([], thresholds=[0.5], margin_steps=-1)


_CRABRO_MISREAD_IMAGE: Sample = (
    [_pred(Species.VESPA_VELUTINA, 0.6)],
    [_truth(Species.VESPA_CRABRO)],
)


def test_false_alert_rate_counts_target_free_images() -> None:
    samples = [_HORNET_IMAGE, _CRABRO_MISREAD_IMAGE, _BEE_MISREAD_IMAGE]
    assert false_alert_rate(samples, 0.3) == 1.0  # both target-free images alert
    assert false_alert_rate(samples, 0.5) == 0.5  # only the 0.6 crabro misread
    assert false_alert_rate(samples, 0.7) == 0.0
    assert false_alert_rate([_HORNET_IMAGE], 0.1) == 0.0  # no target-free image


def test_false_alert_cap_raises_the_threshold() -> None:
    samples = [_HORNET_IMAGE, _CRABRO_MISREAD_IMAGE]
    loose = select_operating_point(samples, thresholds=[0.5, 0.7, 0.9])
    capped = select_operating_point(samples, thresholds=[0.5, 0.7, 0.9], max_false_alert_rate=0.0)
    assert loose.confidence_threshold == 0.5
    assert loose.false_alert_rate == 1.0
    assert capped.confidence_threshold == 0.7
    assert capped.false_alert_rate == 0.0


def _count_samples() -> list[Sample]:
    # Two hornet images (0.3 and 0.6) and two target-free images with a false
    # target box (0.2 and 0.4): image precision is 2/4 at 0.1, 2/3 at 0.3, 1/1 at 0.5.
    return [
        ([_pred(Species.VESPA_VELUTINA, 0.3)], [_truth(Species.VESPA_VELUTINA)]),
        ([_pred(Species.VESPA_VELUTINA, 0.6)], [_truth(Species.VESPA_VELUTINA)]),
        ([_pred(Species.VESPA_VELUTINA, 0.2)], [_truth(Species.APIS_MELLIFERA)]),
        ([_pred(Species.VESPA_VELUTINA, 0.4)], []),
    ]


def test_image_point_counts_flagged_images_not_boxes():
    duplicate = ([_pred(Species.VESPA_VELUTINA, 0.9)] * 3, [_truth(Species.VESPA_VELUTINA)])
    point = image_point([duplicate, *_count_samples()], 0.3)
    assert (point.flagged_positives, point.flagged_negatives, point.positives) == (3, 1, 3)
    assert point.precision == pytest.approx(3 / 4)
    assert point.recall == pytest.approx(1.0)


def test_image_point_without_flags_or_positives_is_zero():
    point = image_point([([], [])], 0.5)
    assert point.precision == 0.0
    assert point.recall == 0.0


def test_count_point_is_the_lowest_threshold_reaching_the_precision():
    point = select_count_point(_count_samples(), [0.5, 0.1, 0.3], 0.6, act_threshold=0.5)
    assert point.confidence_threshold == 0.3


def test_count_point_unreachable_raises():
    samples = _count_samples()
    with pytest.raises(ValueError, match="no threshold"):
        select_count_point(samples, [0.1, 0.3], 0.9, act_threshold=0.5)


def test_count_point_above_act_rejects_the_model():
    samples = _count_samples()
    with pytest.raises(ValueError, match="above the ACT point"):
        select_count_point(samples, [0.1, 0.3, 0.5], 0.9, act_threshold=0.45)
