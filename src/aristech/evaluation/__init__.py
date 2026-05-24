"""Detection evaluation harness (M3).

Pure metrics over predictions vs ground truth — no I/O, no torch — so the
core is unit-tested in CI. Feeding it a real annotated test set (the
dataset half of M3) is a separate, later step.
"""

from aristech.evaluation.metrics import (
    Annotation,
    ClassMetrics,
    EvaluationReport,
    evaluate,
    iou,
)
from aristech.evaluation.operating_point import (
    OperatingPoint,
    ThresholdPoint,
    bees_as_target_count,
    select_operating_point,
    threshold_sweep,
)
from aristech.evaluation.runner import collect_samples, evaluate_on_dataset
from aristech.evaluation.yolo import parse_yolo_labels

__all__ = [
    "Annotation",
    "ClassMetrics",
    "EvaluationReport",
    "OperatingPoint",
    "ThresholdPoint",
    "bees_as_target_count",
    "collect_samples",
    "evaluate",
    "evaluate_on_dataset",
    "iou",
    "parse_yolo_labels",
    "select_operating_point",
    "threshold_sweep",
]
