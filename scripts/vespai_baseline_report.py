"""Recompute the M3 VespAI baseline: per-class precision / recall on a YOLO set.

Runs VespAI once over the given splits with its confidence floor at the
lowest reported threshold, then scores the same
samples at each reported confidence threshold with the M3 harness
(`collect_samples` + `evaluate`) and prints one Markdown table per threshold.
The committed numbers live in ``docs/research/m3-vespai-baseline.md``; this
script is the one command that recomputes them (``make m3-report``).

It needs the `vision` extra, the VespAI weights and the dataset, so it runs
locally, not in CI (weights are CC BY-NC-SA, never committed).

Example:
    python scripts/vespai_baseline_report.py \\
        --weights path/to/yolov5s-all-data.pt \\
        --yolov5-dir path/to/yolov5 \\
        --dataset path/to/roboflow_export
"""

import argparse
import logging
import sys
from collections.abc import Callable
from pathlib import Path

from aristech.application.ports import HornetDetector
from aristech.domain import Species
from aristech.evaluation import EvaluationReport, collect_samples, evaluate

_log = logging.getLogger("aristech.m3_report")

# weights, yolov5_dir, confidence floor -> detector.
DetectorFactory = Callable[[str, str, float], HornetDetector]


def _vespai_factory(weights: str, yolov5_dir: str, floor: float) -> HornetDetector:
    # Imported here so --help and the unit tests work without the `vision` extra.
    from aristech.infrastructure.vision.vespai_detector import VespAIDetector

    return VespAIDetector(weights_path=weights, yolov5_dir=yolov5_dir, confidence=floor)


def _parse_class_map(spec: str) -> dict[int, Species]:
    """Parse ``"0:vespa_crabro,1:vespa_velutina"`` into ``{0: Species, ...}``.

    Raises:
        ValueError: malformed entry, non-integer id or unknown species.
    """
    mapping: dict[int, Species] = {}
    for pair in spec.split(","):
        raw_id, _, raw_species = pair.partition(":")
        if not raw_species:
            raise ValueError(f"bad class-map entry (expected 'id:species'): {pair!r}")
        mapping[int(raw_id)] = Species(raw_species.strip())
    return mapping


def _parse_thresholds(spec: str) -> list[float]:
    """Parse ``"0.5,0.8"``; each value must be in [0, 1]."""
    values = [float(x) for x in spec.split(",")]
    for value in values:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"threshold must be in [0, 1], got {value}")
    return values


def format_markdown(report: EvaluationReport) -> str:
    """One Markdown table of TP / FP / FN / P / R / F1 per class."""
    lines = [
        f"### conf ≥ {report.confidence_threshold:.2f} (IoU ≥ {report.iou_threshold:.2f})",
        "",
        "| class | TP | FP | FN | precision | recall | F1 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for m in report.all_class_metrics():
        lines.append(
            f"| {m.species.value} | {m.tp} | {m.fp} | {m.fn} "
            f"| {m.precision:.3f} | {m.recall:.3f} | {m.f1:.3f} |"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None, detector_factory: DetectorFactory = _vespai_factory) -> int:
    parser = argparse.ArgumentParser(
        prog="vespai_baseline_report",
        description="Recompute VespAI per-class precision/recall on a YOLO dataset.",
    )
    parser.add_argument("--weights", required=True, help="VespAI weights (.pt).")
    parser.add_argument("--yolov5-dir", required=True, help="YOLOv5 clone at the pinned commit.")
    parser.add_argument("--dataset", required=True, help="YOLO dataset root.")
    parser.add_argument("--splits", nargs="+", default=["train", "valid", "test"])
    parser.add_argument("--class-map", default="0:vespa_crabro,1:vespa_velutina")
    parser.add_argument("--iou", type=float, default=0.5)
    parser.add_argument("--thresholds", default="0.5,0.8")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    try:
        class_map = _parse_class_map(args.class_map)
        thresholds = _parse_thresholds(args.thresholds)
    except ValueError as exc:
        _log.error("Invalid argument: %s", exc)
        return 2
    for label, path, check in (
        ("Dataset", args.dataset, Path.is_dir),
        ("Weights", args.weights, Path.is_file),
        ("YOLOv5 directory", args.yolov5_dir, Path.is_dir),
    ):
        if not check(Path(path)):
            _log.error("%s not found: %s", label, path)
            return 2

    # Floor = lowest threshold, not 0: a box below it can never count, and at 0
    # YOLOv5's CPU NMS hits its time limit and silently drops boxes.
    detector = detector_factory(args.weights, args.yolov5_dir, min(thresholds))
    try:
        # One detector pass; every threshold is scored from these samples.
        samples = list(
            collect_samples(detector, Path(args.dataset), class_map, splits=tuple(args.splits))
        )
    except FileNotFoundError as exc:
        _log.error("%s", exc)
        return 2

    images = len(samples)
    truths = sum(len(t) for _p, t in samples)
    print(f"Images: {images} · ground-truth boxes: {truths} · splits: {' '.join(args.splits)}")
    for threshold in thresholds:
        report = evaluate(samples, iou_threshold=args.iou, confidence_threshold=threshold)
        print()
        print(format_markdown(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
