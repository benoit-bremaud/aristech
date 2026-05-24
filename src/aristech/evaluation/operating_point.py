"""Choose the detector's confidence operating point on a labelled set.

The legal floor — never act on a honeybee — drives the choice. The operating
point is the confidence threshold at which **no honeybee is classified as the
target** (`VESPA_VELUTINA`), so the abstention policy never lets a bee through,
while catching as many real hornets as that constraint allows.

Detection is run once upstream (see `runner.collect_samples`, at confidence 0);
this module only re-scores those samples at each candidate threshold, so it is
pure and unit-testable with fakes.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from aristech.domain import Species
from aristech.evaluation.metrics import ClassMetrics, EvaluationReport, Sample, evaluate

# The legal-critical confusion cell: a ground-truth bee predicted as the target.
_BEE = Species.APIS_MELLIFERA.value
_TARGET = Species.VESPA_VELUTINA.value


def bees_as_target_count(report: EvaluationReport) -> int:
    """How many honeybees were classified as the target (`VESPA_VELUTINA`).

    This is the single number the legal floor cares about — it must be zero at
    the chosen operating point.
    """
    return report.confusion.get((_BEE, _TARGET), 0)


@dataclass(frozen=True, slots=True)
class ThresholdPoint:
    """The target species' performance at one confidence threshold."""

    confidence_threshold: float
    target: ClassMetrics  # VESPA_VELUTINA precision / recall at this threshold
    bees_as_target: int


def threshold_sweep(
    samples: Sequence[Sample],
    thresholds: Sequence[float],
    iou_threshold: float = 0.5,
) -> list[ThresholdPoint]:
    """Score the same samples at each confidence threshold.

    `samples` must be a reusable sequence (not a one-shot iterator): it is
    iterated once per threshold. Returns one point per threshold, in order.
    """
    points: list[ThresholdPoint] = []
    for threshold in thresholds:
        report = evaluate(samples, iou_threshold=iou_threshold, confidence_threshold=threshold)
        points.append(
            ThresholdPoint(
                confidence_threshold=threshold,
                target=report.class_metrics(Species.VESPA_VELUTINA),
                bees_as_target=bees_as_target_count(report),
            )
        )
    return points


@dataclass(frozen=True, slots=True)
class OperatingPoint:
    """The chosen confidence threshold and the target metrics it yields.

    `bees_as_target` is zero by construction of `select_operating_point`.
    """

    confidence_threshold: float
    target: ClassMetrics
    bees_as_target: int


def select_operating_point(
    samples: Sequence[Sample],
    thresholds: Sequence[float],
    iou_threshold: float = 0.5,
) -> OperatingPoint:
    """Pick the safe threshold with the best target recall.

    Among the candidate `thresholds` where no honeybee is classified as the
    target, return the one with the highest `VESPA_VELUTINA` recall (catch as
    many hornets as the legal floor permits); ties break toward the **lower**
    threshold. Raises `ValueError` if no threshold drives bees-as-target to
    zero — a signal the detector is unsafe on this set, not something to paper
    over by pushing the threshold ever higher.
    """
    safe = [
        point
        for point in threshold_sweep(samples, thresholds, iou_threshold)
        if point.bees_as_target == 0
    ]
    if not safe:
        raise ValueError(
            "no confidence threshold yields zero honeybees-as-target on this "
            "set; the detector cannot meet the legal floor here"
        )
    best = max(safe, key=lambda p: (p.target.recall, -p.confidence_threshold))
    return OperatingPoint(
        confidence_threshold=best.confidence_threshold,
        target=best.target,
        bees_as_target=best.bees_as_target,
    )
