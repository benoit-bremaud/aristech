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


def false_alert_rate(samples: Sequence[Sample], confidence_threshold: float) -> float:
    """Share of images without a target that still get a target prediction at the threshold.

    An alert is raised per image, not per box, so this is the false-alert cost
    the ACT point is capped on (ADR-0029). 0.0 when no image is target-free.
    """
    negatives = [
        predictions
        for predictions, truths in samples
        if not any(truth.species is Species.VESPA_VELUTINA for truth in truths)
    ]
    if not negatives:
        return 0.0
    alerts = sum(
        1
        for predictions in negatives
        if any(d.is_threat() and d.confidence >= confidence_threshold for d in predictions)
    )
    return alerts / len(negatives)


@dataclass(frozen=True, slots=True)
class ImagePoint:
    """Image-level *V. velutina* figures at one threshold: what an alert weighs (ADR-0029).

    An image is positive when it holds a ground-truth *V. velutina*; it is
    flagged when at least one target prediction reaches the threshold.
    """

    confidence_threshold: float
    flagged_positives: int
    flagged_negatives: int
    positives: int

    @property
    def precision(self) -> float:
        """Share of flagged images that hold a real *V. velutina*; 0.0 when none is flagged."""
        flagged = self.flagged_positives + self.flagged_negatives
        return self.flagged_positives / flagged if flagged else 0.0

    @property
    def recall(self) -> float:
        """Share of images with a *V. velutina* that are flagged; 0.0 without positives."""
        return self.flagged_positives / self.positives if self.positives else 0.0


def image_point(samples: Sequence[Sample], confidence_threshold: float) -> ImagePoint:
    """Score the samples per image at one threshold (see `ImagePoint`)."""
    flagged_positives = flagged_negatives = positives = 0
    for predictions, truths in samples:
        positive = any(truth.species is Species.VESPA_VELUTINA for truth in truths)
        flagged = any(d.is_threat() and d.confidence >= confidence_threshold for d in predictions)
        positives += positive
        flagged_positives += flagged and positive
        flagged_negatives += flagged and not positive
    return ImagePoint(confidence_threshold, flagged_positives, flagged_negatives, positives)


def select_count_point(
    samples: Sequence[Sample],
    thresholds: Sequence[float],
    min_image_precision: float,
    act_threshold: float,
) -> ImagePoint:
    """Pick the COUNT point (ADR-0014, ADR-0031): the lowest threshold whose
    image-level *V. velutina* precision reaches `min_image_precision`.

    Raises `ValueError` when no threshold reaches the target, or when the point
    found lies above `act_threshold`: `COUNT <= ACT` must hold, and a model
    where it does not is rejected (ADR-0014).
    """
    reached = [
        point
        for point in (image_point(samples, t) for t in sorted(thresholds))
        if point.precision >= min_image_precision
    ]
    if not reached:
        raise ValueError(
            f"no threshold reaches an image precision of {min_image_precision:.2f} on this set"
        )
    count = reached[0]
    if count.confidence_threshold > act_threshold:
        raise ValueError(
            f"COUNT point {count.confidence_threshold:.2f} lies above the ACT point "
            f"{act_threshold:.2f}: the model is rejected (ADR-0014)"
        )
    return count


def rule_of_three_bound(trials: int) -> float:
    """95 % upper bound on a rate observed as zero events in `trials` trials (3 / n).

    The "known bound" of ADR-0029: zero bees as target on n bees does not prove
    the rate is zero, only that it is at most 3 / n with 95 % confidence. Valid
    for n of about 30 or more; with no trial at all nothing is known (1.0).
    """
    return min(1.0, 3 / trials) if trials > 0 else 1.0


@dataclass(frozen=True, slots=True)
class OperatingPoint:
    """The chosen confidence threshold and the target metrics it yields.

    `bees_as_target` is zero by construction of `select_operating_point`;
    `bee_count` is the number of ground-truth bees it was measured on.
    """

    confidence_threshold: float
    target: ClassMetrics
    bees_as_target: int
    bee_count: int = 0
    false_alert_rate: float = 0.0

    @property
    def bees_as_target_bound(self) -> float:
        """95 % upper bound on the share of bees classified as target (rule of three)."""
        return rule_of_three_bound(self.bee_count)


def select_operating_point(
    samples: Sequence[Sample],
    thresholds: Sequence[float],
    iou_threshold: float = 0.5,
    margin_steps: int = 0,
    max_false_alert_rate: float = 1.0,
) -> OperatingPoint:
    """Pick the safe threshold with the best target recall.

    Among the candidate `thresholds` where no honeybee is classified as the
    target, return the one with the highest `VESPA_VELUTINA` recall (catch as
    many hornets as the legal floor permits); ties break toward the **lower**
    threshold. Raises `ValueError` if no threshold drives bees-as-target to
    zero — a signal the detector is unsafe on this set, not something to paper
    over by pushing the threshold ever higher.

    `margin_steps` (ADR-0029) also requires the `margin_steps` candidates just
    below a threshold to be safe, so the chosen point sits at least that many
    grid steps above the highest-confidence bee read as target. Pass sorted
    `thresholds` when using it. `max_false_alert_rate` also drops thresholds
    whose image-level `false_alert_rate` exceeds it.
    """
    if margin_steps < 0:
        raise ValueError("margin_steps must be >= 0")
    sweep = threshold_sweep(samples, thresholds, iou_threshold)
    safe = [
        point
        for i, point in enumerate(sweep)
        if i >= margin_steps
        and all(p.bees_as_target == 0 for p in sweep[i - margin_steps : i + 1])
        and false_alert_rate(samples, point.confidence_threshold) <= max_false_alert_rate
    ]
    if not safe:
        raise ValueError(
            "no confidence threshold yields zero honeybees-as-target (with the "
            "margin and false-alert cap) on this set; the detector cannot meet "
            "the legal floor here"
        )
    best = max(safe, key=lambda p: (p.target.recall, -p.confidence_threshold))
    return OperatingPoint(
        confidence_threshold=best.confidence_threshold,
        target=best.target,
        bees_as_target=best.bees_as_target,
        bee_count=sum(
            1
            for _, truths in samples
            for truth in truths
            if truth.species is Species.APIS_MELLIFERA
        ),
        false_alert_rate=false_alert_rate(samples, best.confidence_threshold),
    )
