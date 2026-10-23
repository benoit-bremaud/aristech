"""Score the pre-field RF-DETR model and VespAI on a frozen test set (spec AC7, AC8; ADR-0024).

Runs both detectors once over ``<view>/<test-set id>/`` (written by ``scripts/dataset.py export``,
labels = the committed snapshot) at the lowest threshold, scores each threshold with the UC3
harness and writes one Markdown report: per-class precision / recall side by side, plus the
manifest hash, the frozen-set id and digest, both weights' SHA-256 and their licences.

Needs the `train` extra (RF-DETR), the VespAI weights and YOLOv5 clone, and the images, so it
runs locally, not in CI. VespAI's weights are CC BY-NC-SA: used for comparison only.

Example:
    python scripts/prefield_report.py \\
        --rfdetr-weights data/runs/prefield-small/checkpoint_best_total.pth \\
        --vespai-weights ~/vespai-baseline/vespai/models/yolov5-params/yolov5s-all-data.pt \\
        --yolov5-dir ~/vespai-baseline/yolov5 --out docs/research/prefield-model-test-v1-tables.md
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

from aristech.application.ports import HornetDetector
from aristech.datasets.manifest import CANONICAL_CLASSES, file_sha256
from aristech.datasets.split import FrozenTestSet, load_frozen
from aristech.domain import Species
from aristech.evaluation import EvaluationReport, collect_samples, evaluate

_log = logging.getLogger("aristech.prefield_report")

# Canonical YOLO ids of the frozen-set labels (ADR-0018); "other" is Species.UNKNOWN.
CLASS_MAP: dict[int, Species] = {
    i: Species(name) if name in Species._value2member_map_ else Species.UNKNOWN
    for i, name in enumerate(CANONICAL_CLASSES)
}
LICENCES = {
    "RF-DETR Small (own fine-tune)": "code and base weights Apache-2.0 (rfdetr 1.11.2)",
    "VespAI": "weights CC BY-NC-SA 4.0, YOLOv5 AGPL-3.0 (comparison only)",
}
# name -> detector built at the given confidence floor.
DetectorFactories = Mapping[str, Callable[[float], HornetDetector]]


def view_mismatches(frozen: FrozenTestSet, test_dir: Path) -> list[str]:
    """Images or labels of the exported folder that differ from the frozen set (empty = same)."""
    expected = {r.image_sha256: r.label_sha256 for r in frozen.rows}
    found = {p.stem for p in (test_dir / "images").iterdir()}
    problems = [f"{s[:12]} not in {frozen.id}" for s in sorted(found - expected.keys())]
    problems += [f"{s[:12]} missing from the view" for s in sorted(expected.keys() - found)]
    for sha in sorted(found & expected.keys()):
        label = test_dir / "labels" / f"{sha}.txt"
        if not label.is_file() or file_sha256(label) != expected[sha]:
            problems.append(f"{sha[:12]} label differs from the snapshot")
    return problems


def side_by_side(reports: Mapping[str, EvaluationReport]) -> str:
    """One Markdown table: one row per species, P / R / TP / FP / FN per detector."""
    names = list(reports)
    first = reports[names[0]]
    head = "| class | " + " | ".join(f"{n} P | {n} R | {n} TP/FP/FN" for n in names) + " |"
    lines = [
        f"### conf ≥ {first.confidence_threshold:.2f} (IoU ≥ {first.iou_threshold:.2f})",
        "",
        head,
        "|---|" + "---:|---:|---:|" * len(names),
    ]
    for species in Species:
        cells = []
        for name in names:
            m = reports[name].class_metrics(species)
            cells.append(f"{m.precision:.3f} | {m.recall:.3f} | {m.tp}/{m.fp}/{m.fn}")
        lines.append(f"| {species.value} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def build_report(
    factories: DetectorFactories,
    test_dir: Path,
    thresholds: Sequence[float],
    iou: float,
    provenance: Sequence[tuple[str, str]],
) -> str:
    """Run every detector once at the lowest threshold, score each threshold, return Markdown."""
    floor = min(thresholds)
    samples = {
        name: list(
            collect_samples(make(floor), test_dir.parent, CLASS_MAP, splits=(test_dir.name,))
        )
        for name, make in factories.items()
    }
    first = next(iter(samples.values()))
    lines = ["# Pre-field model on the frozen test set", ""]
    lines += [f"- {key}: {value}" for key, value in provenance]
    lines += [
        f"- images: {len(first)} · ground-truth boxes: {sum(len(t) for _p, t in first)}",
        "",
    ]
    for threshold in thresholds:
        reports = {
            name: evaluate(s, iou_threshold=iou, confidence_threshold=threshold)
            for name, s in samples.items()
        }
        lines += [side_by_side(reports), ""]
    return "\n".join(lines)


def _rfdetr(weights: str) -> Callable[[float], HornetDetector]:
    def make(floor: float) -> HornetDetector:
        from aristech.infrastructure.vision.rfdetr_detector import RFDETRDetector

        return RFDETRDetector(checkpoint_path=weights, confidence=floor)

    return make


def _vespai(weights: str, yolov5_dir: str) -> Callable[[float], HornetDetector]:
    def make(floor: float) -> HornetDetector:
        from aristech.infrastructure.vision.vespai_detector import VespAIDetector

        return VespAIDetector(weights_path=weights, yolov5_dir=yolov5_dir, confidence=floor)

    return make


def main(argv: Sequence[str] | None = None, factories: DetectorFactories | None = None) -> int:
    """Check the inputs, build the report, write it; return the exit code."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--registry", type=Path, default=Path("data/registry"))
    parser.add_argument("--view", type=Path, default=Path("data/views/prefield"))
    parser.add_argument("--test-set", default="test-v1")
    parser.add_argument("--rfdetr-weights", type=Path, required=True)
    parser.add_argument("--vespai-weights", type=Path, required=True)
    parser.add_argument("--yolov5-dir", type=Path, required=True)
    parser.add_argument("--thresholds", default="0.5,0.8")
    parser.add_argument("--iou", type=float, default=0.5)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    try:
        thresholds = [float(x) for x in args.thresholds.split(",")]
        if not all(0.0 <= t <= 1.0 for t in thresholds):
            raise ValueError(f"thresholds must be in [0, 1]: {args.thresholds}")
        frozen = load_frozen(args.registry / f"{args.test_set}.csv")
        test_dir = args.view / args.test_set
        for label, path in (
            ("test images", test_dir / "images"),
            ("RF-DETR weights", args.rfdetr_weights),
            ("VespAI weights", args.vespai_weights),
            ("YOLOv5 directory", args.yolov5_dir),
        ):
            if not path.exists():
                raise FileNotFoundError(f"{label} not found: {path}")
        if not args.out.parent.is_dir():
            raise FileNotFoundError(f"report directory not found: {args.out.parent}")
        mismatches = view_mismatches(frozen, test_dir)
        if mismatches:
            raise ValueError(f"{test_dir} is stale, re-run export: " + "; ".join(mismatches[:5]))
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    chosen = factories or {
        "RF-DETR": _rfdetr(str(args.rfdetr_weights)),
        "VespAI": _vespai(str(args.vespai_weights), str(args.yolov5_dir)),
    }
    provenance = [
        ("frozen set", f"{frozen.id} ({len(frozen.rows)} images), sha256 {frozen.digest()}"),
        ("manifest sha256", file_sha256(args.registry / "manifest.csv")),
        ("RF-DETR weights sha256", file_sha256(args.rfdetr_weights)),
        ("VespAI weights sha256", file_sha256(args.vespai_weights)),
        *LICENCES.items(),
    ]
    text = build_report(chosen, test_dir, thresholds, args.iou, provenance)
    args.out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
