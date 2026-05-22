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
from aristech.evaluation.runner import evaluate_on_dataset
from aristech.evaluation.yolo import parse_yolo_labels

__all__ = [
    "Annotation",
    "ClassMetrics",
    "EvaluationReport",
    "evaluate",
    "evaluate_on_dataset",
    "iou",
    "parse_yolo_labels",
]
