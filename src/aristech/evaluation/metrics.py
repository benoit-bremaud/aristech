"""Pure detection-evaluation metrics: IoU, greedy location-based matching,
per-class precision / recall / F1, and a confusion matrix.

A prediction is a domain `Detection`; a ground-truth box is an `Annotation`.
Both boxes must be in the same coordinate space (all pixels, or all
normalised). The `background` label captures false positives (a prediction
matching no ground truth) and misses (a ground truth matching no prediction).
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from aristech.domain import BoundingBox, Detection, Species

BACKGROUND = "background"

# Per image: the predictions and the ground-truth boxes for that image.
Sample = tuple[Sequence[Detection], Sequence["Annotation"]]


@dataclass(frozen=True, slots=True)
class Annotation:
    """A ground-truth box: a species at a location, no confidence."""

    species: Species
    bbox: BoundingBox


def iou(a: BoundingBox, b: BoundingBox) -> float:
    """Intersection-over-union of two boxes in the same coordinate space."""
    ix1, iy1 = max(a.x, b.x), max(a.y, b.y)
    ix2 = min(a.x + a.width, b.x + b.width)
    iy2 = min(a.y + a.height, b.y + b.height)
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    union = a.area + b.area - inter
    return inter / union if union > 0 else 0.0


@dataclass(frozen=True, slots=True)
class ClassMetrics:
    species: Species
    tp: int
    fp: int
    fn: int

    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        return self.tp / denom if denom else 0.0

    @property
    def recall(self) -> float:
        denom = self.tp + self.fn
        return self.tp / denom if denom else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0


def _match_image(
    predictions: Sequence[Detection],
    truths: Sequence[Annotation],
    iou_threshold: float,
) -> Iterable[tuple[str, str]]:
    """Greedily match predictions (highest confidence first) to the
    best-IoU unused ground-truth box. Yields ``(true_label, pred_label)``
    pairs, using ``BACKGROUND`` for unmatched predictions and misses."""
    used: set[int] = set()
    ordered = sorted(predictions, key=lambda d: d.confidence, reverse=True)
    for pred in ordered:
        best_idx: int | None = None
        best_iou = iou_threshold
        for i, truth in enumerate(truths):
            if i in used:
                continue
            value = iou(pred.bbox, truth.bbox)
            if value >= best_iou:
                best_iou = value
                best_idx = i
        if best_idx is None:
            yield (BACKGROUND, pred.species.value)
        else:
            used.add(best_idx)
            yield (truths[best_idx].species.value, pred.species.value)
    for i, truth in enumerate(truths):
        if i not in used:
            yield (truth.species.value, BACKGROUND)


@dataclass(frozen=True)
class EvaluationReport:
    confusion: dict[tuple[str, str], int]
    iou_threshold: float
    confidence_threshold: float

    def class_metrics(self, species: Species) -> ClassMetrics:
        label = species.value
        tp = self.confusion.get((label, label), 0)
        fp = sum(c for (t, p), c in self.confusion.items() if p == label and t != label)
        fn = sum(c for (t, p), c in self.confusion.items() if t == label and p != label)
        return ClassMetrics(species=species, tp=tp, fp=fp, fn=fn)

    def all_class_metrics(self) -> list[ClassMetrics]:
        seen = {t for t, _ in self.confusion} | {p for _, p in self.confusion}
        species = [s for s in Species if s.value in seen]
        return [self.class_metrics(s) for s in species]

    def format_text(self) -> str:
        lines = [
            f"Evaluation (IoU>={self.iou_threshold:.2f}, conf>={self.confidence_threshold:.2f})",
            f"{'class':<16}{'P':>8}{'R':>8}{'F1':>8}{'TP':>6}{'FP':>6}{'FN':>6}",
        ]
        for m in self.all_class_metrics():
            lines.append(
                f"{m.species.value:<16}{m.precision:>8.3f}{m.recall:>8.3f}"
                f"{m.f1:>8.3f}{m.tp:>6}{m.fp:>6}{m.fn:>6}"
            )
        return "\n".join(lines)


def evaluate(
    samples: Iterable[Sample],
    iou_threshold: float = 0.5,
    confidence_threshold: float = 0.0,
) -> EvaluationReport:
    """Build an `EvaluationReport` from per-image (predictions, truths).
    Predictions below `confidence_threshold` are dropped first."""
    if not 0.0 < iou_threshold <= 1.0:
        raise ValueError(f"iou_threshold must be in (0, 1], got {iou_threshold}")
    if not 0.0 <= confidence_threshold <= 1.0:
        raise ValueError(f"confidence_threshold must be in [0, 1], got {confidence_threshold}")
    confusion: dict[tuple[str, str], int] = {}
    for predictions, truths in samples:
        kept = [d for d in predictions if d.confidence >= confidence_threshold]
        for pair in _match_image(kept, truths, iou_threshold):
            confusion[pair] = confusion.get(pair, 0) + 1
    return EvaluationReport(
        confusion=confusion,
        iou_threshold=iou_threshold,
        confidence_threshold=confidence_threshold,
    )
