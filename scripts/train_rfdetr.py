"""Fine-tune RF-DETR Small on the train and validation splits of the manifest (ADR-0022, ADR-0024).

Re-exports the YOLO view first, so the frozen-set checks run right before training (spec AC5):
any violation stops with exit 2 and nothing is trained. Needs the `train` extra and a GPU, so it
runs locally, not in CI. The checkpoint stays git-ignored; its SHA-256 is printed for the report.

Example:
    python scripts/train_rfdetr.py --store data/dataset --view data/views/prefield \\
        --output data/runs/prefield-small --epochs 40
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from aristech.datasets.export import export_yolo_view
from aristech.datasets.manifest import file_sha256, read_manifest
from aristech.datasets.registry import LicenceError, load_register, require
from aristech.datasets.split import FrozenSetViolation, discover_frozen

_log = logging.getLogger("aristech.train")

# dataset_dir, output_dir, epochs -> None (trains and writes checkpoints into output_dir).
Trainer = Callable[[Path, Path, int], None]
BEST_CHECKPOINT = "checkpoint_best_total.pth"


def _train_small(view: Path, output: Path, epochs: int) -> None:
    # Imported here so --help and the unit tests work without the `train` extra.
    from rfdetr import RFDETRSmall

    RFDETRSmall().train(
        dataset_dir=str(view),
        output_dir=str(output),
        epochs=epochs,
        batch_size="auto",
        early_stopping=True,
    )


def main(argv: Sequence[str] | None = None, trainer: Trainer = _train_small) -> int:
    """Export the view, train, print the best checkpoint's hash.

    Exit 0 on success, 1 if training wrote no best checkpoint, 2 on a bad argument, a refused
    licence, a frozen-set violation or a missing / non-view path.
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--registry", type=Path, default=Path("data/registry"))
    parser.add_argument("--store", type=Path, default=Path("data/dataset"))
    parser.add_argument("--view", type=Path, default=Path("data/views/prefield"))
    parser.add_argument("--output", type=Path, required=True, help="git-ignored run directory")
    parser.add_argument("--epochs", type=int, default=40)
    args = parser.parse_args(argv)
    if args.epochs < 1:
        print("error: --epochs must be at least 1", file=sys.stderr)
        return 2
    try:
        sources = load_register(args.registry / "licences.csv")
        rows = read_manifest(args.registry / "manifest.csv")
        for source_id in sorted({r.source_id for r in rows}):
            require(sources, source_id)
        counts = export_yolo_view(
            rows, discover_frozen(args.registry), args.store, args.registry, args.view
        )
    except FrozenSetViolation as exc:
        for line in exc.violations:
            print(f"violation: {line}", file=sys.stderr)
        return 2
    except (LicenceError, ValueError, FileNotFoundError, FileExistsError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    _log.info("view %s: %s", args.view, counts)
    trainer(args.view, args.output, args.epochs)
    best = args.output / BEST_CHECKPOINT
    if not best.is_file():
        print(f"error: training wrote no {best}", file=sys.stderr)
        return 1
    print(f"best checkpoint {best} sha256 {file_sha256(best)}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
