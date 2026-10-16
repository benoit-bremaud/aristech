"""`aristech` command line: configuration, logging and the composition root."""

import argparse
import logging
import logging.config
import sys
from pathlib import Path
from typing import Any, cast

import yaml

# Detector floor: boxes between it and --confidence reach decide() as ABSTAIN (ADR-0009).
_DEFAULT_DETECTOR_FLOOR = 0.1


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must hold a YAML mapping, not {type(data).__name__}")
    return cast(dict[str, Any], data)


def main(argv: list[str] | None = None) -> int:
    """Parse the arguments and run detection on `--video`; returns the exit code."""
    parser = argparse.ArgumentParser(prog="aristech")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/config.yaml"),
        help="Path to the application configuration file.",
    )
    parser.add_argument(
        "--logging-config",
        type=Path,
        default=Path("config/logging.yaml"),
        help="Path to the logging configuration file.",
    )
    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="Video source to analyse (file or camera index). Needs the 'vision' extra.",
    )
    parser.add_argument(
        "--weights",
        type=str,
        default=None,
        help="Path to the VespAI weights (.pt). Required with --video.",
    )
    parser.add_argument(
        "--yolov5-dir",
        type=str,
        default=None,
        help="Path to the local YOLOv5 clone (VespAI submodule). Required with --video.",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.5,
        help="ACT/ABSTAIN operating threshold (0-1), see ADR-0004.",
    )
    parser.add_argument(
        "--detector-floor",
        type=float,
        default=None,
        help=(
            "Detector confidence floor (0-1, <= --confidence). "
            "Default: min(0.1, --confidence). See ADR-0009."
        ),
    )
    args = parser.parse_args(argv)

    if args.logging_config.exists():
        # Logging setup must never crash the app: bad YAML (YAMLError) or a
        # malformed dictConfig (Type/Key/Attribute/Import/Value/OSError) all
        # fall back to a working basic configuration.
        try:
            logging.config.dictConfig(_load_yaml(args.logging_config))
        except Exception as exc:  # noqa: BLE001 — intentional logging fallback
            logging.basicConfig(level=logging.INFO)
            logging.getLogger("aristech").warning(
                "Unusable logging config (%s), falling back to basicConfig.", exc
            )
    else:
        logging.basicConfig(level=logging.INFO)

    log = logging.getLogger("aristech")

    if not args.config.exists():
        log.error("Configuration not found: %s", args.config)
        return 2

    config = _load_yaml(args.config)
    log.info("aristech started, version %s", config.get("app", {}).get("version", "?"))

    if args.video is None:
        log.warning("No video source (--video): nothing to analyse.")
        return 0

    return _run_visual_detection(args, log)


def _run_visual_detection(args: argparse.Namespace, log: logging.Logger) -> int:
    """Composition root: build the vision adapters and run `DetectHornetVisual`.
    Imports are local so the base CLI works without the `vision` extra."""
    if args.weights is None or args.yolov5_dir is None:
        log.error("--video needs --weights and --yolov5-dir.")
        return 2

    if not 0.0 <= args.confidence <= 1.0:
        log.error("--confidence must be in [0, 1] (got %s).", args.confidence)
        return 2

    floor = (
        min(_DEFAULT_DETECTOR_FLOOR, args.confidence)
        if args.detector_floor is None
        else args.detector_floor
    )
    if not 0.0 <= floor <= args.confidence:
        log.error(
            "--detector-floor must be in [0, --confidence] (got %s, --confidence %s).",
            floor,
            args.confidence,
        )
        return 2

    # A bare digit with no matching file is a camera index; otherwise it is a
    # file path that must exist (a file literally named "0" stays a path).
    video_path = Path(args.video)
    if args.video.isdigit() and not video_path.exists():
        source: str | int = int(args.video)
    elif not video_path.exists():
        log.error("Video source not found: %s", args.video)
        return 2
    else:
        source = args.video

    if not Path(args.weights).is_file():
        log.error("Weights not found: %s", args.weights)
        return 2
    if not Path(args.yolov5_dir).is_dir():
        log.error("YOLOv5 directory not found: %s", args.yolov5_dir)
        return 2

    from aristech.application.use_cases import (
        DetectHornetVisual,
        DetectHornetVisualConfig,
    )
    from aristech.infrastructure.notify.logging_notifier import LoggingNotifier
    from aristech.infrastructure.vision.opencv_video_source import OpenCVVideoSource
    from aristech.infrastructure.vision.vespai_detector import VespAIDetector

    use_case = DetectHornetVisual(
        video=OpenCVVideoSource(source),
        detector=VespAIDetector(
            weights_path=args.weights,
            yolov5_dir=args.yolov5_dir,
            confidence=floor,
        ),
        notifier=LoggingNotifier(),
        config=DetectHornetVisualConfig(confidence_threshold=args.confidence),
    )
    result = use_case.run()
    log.info(
        "Analysis done: %d threat(s), %d abstention(s) below the threshold.",
        result.threats,
        result.abstentions,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
