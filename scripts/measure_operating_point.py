"""Measure the detector's confidence operating point on an annotated set.

Runs VespAI once over a YOLO-format dataset at confidence 0 (so the whole
prediction range is available), sweeps candidate confidence thresholds, and
prints both the per-threshold curve and the selected operating point — the
lowest threshold at which **no honeybee is classified as the target**
(`VESPA_VELUTINA`), with the best hornet recall under that legal-floor zero.

This is the M4 "verified on the set" step. It needs the `vision` extra
(torch + opencv), the VespAI weights (operator-supplied; not in the repo), and
the annotated dataset — so it runs locally, not in CI.

Example:
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

from aristech.domain import Species
from aristech.evaluation import (
    collect_samples,
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="measure_operating_point",
        description="Sweep VespAI confidence thresholds and pick the legal-floor "
        "operating point on a YOLO dataset.",
    )
    parser.add_argument("--weights", required=True, help="Poids VespAI (.pt).")
    parser.add_argument(
        "--yolov5-dir", required=True, help="Clone local YOLOv5 (sous-module VespAI)."
    )
    parser.add_argument("--dataset", required=True, help="Racine du dataset YOLO.")
    parser.add_argument(
        "--splits",
        nargs="+",
        default=["test"],
        help="Splits à évaluer (ex: test valid). Défaut: test.",
    )
    parser.add_argument(
        "--class-map",
        required=True,
        help="Map id→espèce, ex: '0:vespa_crabro,1:vespa_velutina,2:apis_mellifera'.",
    )
    parser.add_argument(
        "--iou", type=float, default=0.5, help="Seuil IoU d'appariement (défaut 0.5)."
    )
    parser.add_argument(
        "--thresholds",
        default=None,
        help="Liste de seuils à balayer (ex: '0.3,0.5,0.7'). Défaut: 0.05→0.95.",
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
    if not Path(args.yolov5_dir).is_dir():
        _log.error("Répertoire YOLOv5 introuvable : %s", args.yolov5_dir)
        return 2

    # Imported here so --help works without the `vision` extra installed.
    from aristech.infrastructure.vision.vespai_detector import VespAIDetector

    # confidence=0.0 is mandatory: the detector must emit every prediction so
    # the sweep sees the full range (see evaluation.collect_samples).
    detector = VespAIDetector(weights_path=args.weights, yolov5_dir=args.yolov5_dir, confidence=0.0)

    _log.info("Running VespAI over %s (splits=%s)…", dataset, args.splits)
    samples = list(collect_samples(detector, dataset, class_map, splits=tuple(args.splits)))
    _log.info("Scored %d image(s).", len(samples))

    bees = _count_truth_bees(samples)
    if bees == 0:
        _log.warning(
            "⚠ No honeybee (APIS_MELLIFERA) ground-truth box in this set: "
            "bees-as-target is trivially 0, so the legal-floor gate is NOT "
            "actually exercised here. Use a set that contains bees to verify it."
        )

    _log.info("\n%-10s %8s %8s %8s %14s", "conf", "P", "R", "F1", "bees→target")
    for point in threshold_sweep(samples, thresholds, iou_threshold=args.iou):
        m = point.target
        _log.info(
            "%-10.2f %8.3f %8.3f %8.3f %14d",
            point.confidence_threshold,
            m.precision,
            m.recall,
            m.f1,
            point.bees_as_target,
        )

    try:
        chosen = select_operating_point(samples, thresholds, iou_threshold=args.iou)
    except ValueError as exc:
        _log.error("\nNo safe operating point: %s", exc)
        return 1

    _log.info(
        "\n✓ Operating point: confidence_threshold=%.2f "
        "(V. velutina P=%.3f R=%.3f, bees→target=%d)",
        chosen.confidence_threshold,
        chosen.target.precision,
        chosen.target.recall,
        chosen.bees_as_target,
    )
    _log.info(
        "Wire this into config/config.yaml (hornet_detection.confidence_threshold) "
        "and DetectHornetVisualConfig.confidence_threshold."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
