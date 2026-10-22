"""Dataset CLI: import a licensed source, split by group, freeze a test-set version.

Spec ``docs/architecture/specs/annotation-pipeline.md``; ADR-0018 to ADR-0020. The registry
(``data/registry/``: licences, manifest, frozen sets) is committed; the image store
(``data/dataset/``) is git-ignored. Exit code 2 on a refused licence, an unmapped class, a
frozen-set violation or an existing frozen version.

Example:
    python scripts/dataset.py import --source roboflow-hornet-behavior-v1 \\
        --dir data/external/vespa-crabro-velutina --class-map 0:1,1:0
    python scripts/dataset.py split --seed 0
    python scripts/dataset.py freeze --id test-v1
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

from aristech.datasets.manifest import (
    ManifestRow,
    import_yolo_source,
    merge_rows,
    read_manifest,
    write_manifest,
)
from aristech.datasets.registry import LicenceError, load_register, require
from aristech.datasets.split import FrozenSetViolation, freeze, load_frozen, split_by_group

_log = logging.getLogger("aristech.dataset")


def _class_map(text: str) -> dict[int, int]:
    try:
        pairs = (item.split(":") for item in text.split(",") if item)
        return {int(src): int(dst) for src, dst in pairs}
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"--class-map must look like 0:1,1:0, got {text!r}"
        ) from exc


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--registry", type=Path, default=Path("data/registry"))
    parser.add_argument("--store", type=Path, default=Path("data/dataset"))
    commands = parser.add_subparsers(dest="command", required=True)
    imp = commands.add_parser("import", help="import a YOLO export of a registered source")
    imp.add_argument("--source", required=True)
    imp.add_argument("--dir", type=Path, required=True)
    imp.add_argument("--class-map", type=_class_map, required=True, help="source id:canonical id,…")
    spl = commands.add_parser("split", help="assign train/validation/test by group")
    spl.add_argument("--seed", type=int, default=0)
    spl.add_argument("--frozen", type=Path, help="frozen test set to respect (test-vN.csv)")
    frz = commands.add_parser("freeze", help="freeze the current test rows as a new version")
    frz.add_argument("--id", required=True, help="e.g. test-v1")
    return parser


def _summary(rows: Sequence[ManifestRow]) -> str:
    counts = Counter(r.split.value for r in rows)
    return ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))


def main(argv: Sequence[str] | None = None) -> int:
    """Run one subcommand; return the process exit code."""
    args = _parser().parse_args(argv)
    manifest_path = args.registry / "manifest.csv"
    try:
        sources = load_register(args.registry / "licences.csv")
        if args.command == "import":
            source = require(sources, args.source)
            if not args.dir.is_dir():
                raise ValueError(f"{args.dir} is not a directory")
            incoming = import_yolo_source(source, args.dir, args.class_map, args.store)
            rows = merge_rows(read_manifest(manifest_path), incoming)
            write_manifest(manifest_path, rows)
            print(f"imported {len(incoming)} images from {source.id}; manifest has {len(rows)}")
        elif args.command == "split":
            frozen = load_frozen(args.frozen) if args.frozen else None
            captive = frozenset(s.id for s in sources.values() if s.captive)
            rows = split_by_group(
                read_manifest(manifest_path), seed=args.seed, frozen=frozen, captive_sources=captive
            )
            write_manifest(manifest_path, rows)
            print(f"split (seed {args.seed}): {_summary(rows)}")
        else:
            frozen_set = freeze(args.id, read_manifest(manifest_path), args.registry, args.store)
            print(
                f"froze {frozen_set.id}: {len(frozen_set.rows)} images, "
                f"sha256 {frozen_set.digest()}"
            )
    except FrozenSetViolation as exc:
        for line in exc.violations:
            print(f"violation: {line}", file=sys.stderr)
        return 2
    except (LicenceError, ValueError, FileExistsError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
