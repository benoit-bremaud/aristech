"""Measure the detector's confidence operating point on an annotated set.

Runs a detector (RF-DETR checkpoint or VespAI) once over a YOLO-format dataset
at confidence 0 (so the whole prediction range is available), sweeps candidate
confidence thresholds, and prints both the per-threshold curve and the
selected operating point — the lowest threshold at which **no honeybee is classified as the target**
(`VESPA_VELUTINA`), one grid step of margin above the last unsafe threshold
(ADR-0029), with the 95 % rule-of-three bound on the bees-as-target rate.

This is the M4 "verified on the set" step. It needs the `train` extra
(RF-DETR) or the `vision` extra and VespAI weights (operator-supplied; not in
the repo), and the annotated dataset — so it runs locally, not in CI.

Example (RF-DETR on the frozen test set, canonical class ids):
    python scripts/measure_operating_point.py --detector rfdetr \\
        --weights data/runs/prefield-small/checkpoint_best_total.pth \\
        --dataset data/views/prefield --splits test-v1 \\
        --class-map 0:vespa_velutina,1:vespa_crabro,2:apis_mellifera,3:unknown

Example (VespAI):
    python scripts/measure_operating_point.py \\
        --weights path/to/vespai.pt \\
        --yolov5-dir path/to/yolov5 \\
        --dataset path/to/roboflow_export \\
        --splits test valid \\
        --class-map 0:vespa_crabro,1:vespa_velutina,2:apis_mellifera
"""

import argparse
import logging
import sys
from pathlib import Path

from aristech.application.ports import HornetDetector
from aristech.domain import Species
from aristech.evaluation import (
    collect_samples,
    false_alert_rate,
    select_operating_point,
    threshold_sweep,
)
from aristech.evaluation.metrics import Sample

_log = logging.getLogger("aristech.measure")


def _parse_class_map(spec: str) -> dict[int, Species]:
    """Parse ``"0:vespa_crabro,1:vespa_velutina"`` into ``{0: Species, ...}``.

    Values must match `Species` enum values; ids must be integers. The map
    must contain `vespa_velutina` (the target species).

    Raises:
        ValueError: malformed entry, non-integer id, unknown species, or no
            `vespa_velutina` mapping.
    """
    mapping: dict[int, Species] = {}
    for pair in spec.split(","):
        raw_id, _, raw_species = pair.partition(":")
        if not raw_species:
            raise ValueError(f"bad class-map entry (expected 'id:species'): {pair!r}")
        mapping[int(raw_id)] = Species(raw_species.strip())
    if Species.VESPA_VELUTINA not in mapping.values():
        raise ValueError("class-map must map an id to 'vespa_velutina' (the target species)")
    return mapping


def _parse_thresholds(spec: str | None) -> list[float]:
    """Parse a comma list, or default to 0.05 … 0.95 in 0.05 steps."""
    if spec:
        return [float(x) for x in spec.split(",")]
    return [round(0.05 * i, 2) for i in range(1, 20)]


def _count_truth_bees(samples: list[Sample]) -> int:
    return sum(
        1
        for _predictions, truths in samples
        for truth in truths
        if truth.species is Species.APIS_MELLIFERA
    )


def _build_detector(kind: str, weights: str, yolov5_dir: str | None) -> HornetDetector:
    """Build the detector at confidence 0 so the sweep sees every prediction.

    Imported lazily so --help works without the heavy extras installed.
    """
    if kind == "rfdetr":
        from aristech.infrastructure.vision.rfdetr_detector import RFDETRDetector

        return RFDETRDetector(checkpoint_path=weights, confidence=0.0)
    from aristech.infrastructure.vision.vespai_detector import VespAIDetector

    return VespAIDetector(weights_path=weights, yolov5_dir=str(yolov5_dir), confidence=0.0)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="measure_operating_point",
        description="Sweep detector confidence thresholds and pick the legal-floor "
        "operating point on a YOLO dataset.",
    )
    parser.add_argument(
        "--detector", choices=("vespai", "rfdetr"), default="vespai", help="Default: vespai."
    )
    parser.add_argument("--weights", required=True, help="VespAI .pt or RF-DETR checkpoint.")
    parser.add_argument("--yolov5-dir", help="Local YOLOv5 clone (VespAI only).")
    parser.add_argument(
        "--max-false-alert-rate",
        type=float,
        default=0.025,
        help="Cap on the share of target-free images that raise an alert (ADR-0029). "
        "Default: 0.025.",
    )
    parser.add_argument(
        "--margin-steps",
        type=int,
        default=1,
        help="Safe grid steps required below the chosen threshold (ADR-0029). Default: 1.",
    )
    parser.add_argument("--dataset", required=True, help="YOLO dataset root.")
    parser.add_argument(
        "--splits",
        nargs="+",
        default=["test"],
        help="Splits to evaluate (e.g. test valid). Default: test.",
    )
    parser.add_argument(
        "--class-map",
        required=True,
        help="Class id to species map, e.g. '0:vespa_crabro,1:vespa_velutina,2:apis_mellifera'.",
    )
    parser.add_argument(
        "--iou", type=float, default=0.5, help="IoU matching threshold (default 0.5)."
    )
    parser.add_argument(
        "--thresholds",
        default=None,
        help="Thresholds to sweep (e.g. '0.3,0.5,0.7'). Default: 0.05→0.95.",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    try:
        class_map = _parse_class_map(args.class_map)
        thresholds = _parse_thresholds(args.thresholds)
    except ValueError as exc:
        _log.error("Argument invalide : %s", exc)
        return 2
    if Species.APIS_MELLIFERA not in class_map.values():
        _log.warning(
            "⚠ class-map has no 'apis_mellifera' id: bees-as-target will be "
            "vacuously 0 and the legal-floor gate is NOT exercised."
        )

    dataset = Path(args.dataset)
    if not dataset.is_dir():
        _log.error("Dataset introuvable : %s", dataset)
        return 2
    if not Path(args.weights).is_file():
        _log.error("Poids introuvables : %s", args.weights)
        return 2
    if args.detector == "vespai" and not (args.yolov5_dir and Path(args.yolov5_dir).is_dir()):
        _log.error("YOLOv5 directory not found: %s", args.yolov5_dir)
        return 2

    detector = _build_detector(args.detector, args.weights, args.yolov5_dir)

    _log.info("Running %s over %s (splits=%s)…", args.detector, dataset, args.splits)
    samples = list(collect_samples(detector, dataset, class_map, splits=tuple(args.splits)))
    _log.info("Scored %d image(s).", len(samples))

    bees = _count_truth_bees(samples)
    if bees == 0:
        _log.warning(
            "⚠ No honeybee (APIS_MELLIFERA) ground-truth box in this set: "
            "bees-as-target is trivially 0, so the legal-floor gate is NOT "
            "actually exercised here. Use a set that contains bees to verify it."
        )

    _log.info(
        "\n%-10s %8s %8s %8s %14s %12s", "conf", "P", "R", "F1", "bees→target", "false alerts"
    )
    for point in threshold_sweep(samples, thresholds, iou_threshold=args.iou):
        m = point.target
        _log.info(
            "%-10.2f %8.3f %8.3f %8.3f %14d %12.3f",
            point.confidence_threshold,
            m.precision,
            m.recall,
            m.f1,
            point.bees_as_target,
            false_alert_rate(samples, point.confidence_threshold),
        )

    try:
        chosen = select_operating_point(
            samples,
            thresholds,
            iou_threshold=args.iou,
            margin_steps=args.margin_steps,
            max_false_alert_rate=args.max_false_alert_rate,
        )
    except ValueError as exc:
        _log.error("\nNo safe operating point: %s", exc)
        return 1

    _log.info(
        "\n✓ Operating point: confidence_threshold=%.2f "
        "(V. velutina P=%.3f R=%.3f, bees→target=%d of %d bees, "
        "95 %% bound ≤ %.2f %%, false alerts %.1f %% of images)",
        chosen.confidence_threshold,
        chosen.target.precision,
        chosen.target.recall,
        chosen.bees_as_target,
        chosen.bee_count,
        100 * chosen.bees_as_target_bound,
        100 * chosen.false_alert_rate,
    )
    _log.info("Pass it to the CLI as --confidence (DetectHornetVisualConfig.confidence_threshold).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
