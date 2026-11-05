"""`aristech` command line: configuration, logging and the composition root."""

import argparse
import hashlib
import logging
import logging.config
import statistics
import sys
import time
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import yaml

from aristech import __version__

if TYPE_CHECKING:
    from aristech.application.attack_episode import EpisodeRule
    from aristech.application.health import HealthRule
    from aristech.application.ports import HornetDetector, Notifier
    from aristech.domain import Detection, VideoFrame

# Detector floor: boxes between it and --confidence reach decide() as ABSTAIN (ADR-0009).
_DEFAULT_DETECTOR_FLOOR = 0.1

# Default operating threshold per detector (ADR-0030). The RF-DETR value is the ACT point of
# ADR-0029, measured on test-v1 for the checkpoint with this sha256 only.
_DEFAULT_CONFIDENCE = {"vespai": 0.5, "rfdetr": 0.45}
# Default COUNT point per detector (ADR-0031), same checkpoint caveat; VespAI has none
# measured, so it counts at its ACT point.
_DEFAULT_COUNT_CONFIDENCE = {"vespai": 0.5, "rfdetr": 0.15}
_RFDETR_MEASURED_SHA256 = "3df5a250d9cf3dc837a86376b62b634d0f693d202288a782bd46cb8cf992fcab"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


class _TimedDetector:
    """`HornetDetector` decorator that records the wall-clock latency of every `detect` call."""

    def __init__(self, inner: "HornetDetector") -> None:
        self._inner = inner
        self.latencies: list[float] = []

    def detect(self, frame: "VideoFrame") -> "Sequence[Detection]":
        start = time.perf_counter()
        try:
            return self._inner.detect(frame)
        finally:
            self.latencies.append(time.perf_counter() - start)


def _log_timing(log: logging.Logger, latencies: list[float], elapsed: float) -> None:
    """Log FPS and detect latency. The first call loads the model (lazy adapters), so it is
    reported apart as warm-up and left out of the steady-state figures."""
    if len(latencies) < 2:
        log.info("Timing: %d frame(s), too few for a steady-state figure.", len(latencies))
        return
    warm_up, steady = latencies[0], sorted(latencies[1:])
    steady_elapsed = elapsed - warm_up
    p95 = steady[min(len(steady) - 1, int(0.95 * len(steady)))]
    log.info(
        "Timing: %d frame(s), warm-up %.1f s, then %.2f FPS end to end, "
        "detect latency p50 %.1f ms, p95 %.1f ms.",
        len(latencies),
        warm_up,
        len(steady) / steady_elapsed if steady_elapsed > 0 else 0.0,
        statistics.median(steady) * 1000,
        p95 * 1000,
    )


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must hold a YAML mapping, not {type(data).__name__}")
    return cast(dict[str, Any], data)


def _ensure_log_dirs(logging_config: dict[str, Any]) -> None:
    """Create the parent folder of every file handler, so a fresh checkout without `logs/`
    still gets its log file (#143)."""
    for handler in logging_config.get("handlers", {}).values():
        if isinstance(handler, dict) and "filename" in handler:
            Path(handler["filename"]).parent.mkdir(parents=True, exist_ok=True)


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
        "--detector",
        choices=sorted(_DEFAULT_CONFIDENCE),
        default="vespai",
        help="Detector to run with --video (ADR-0030); rfdetr also needs the 'train' extra.",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=None,
        help="Path to the RF-DETR checkpoint (.pth). Required with --detector rfdetr.",
    )
    parser.add_argument(
        "--weights",
        type=str,
        default=None,
        help="Path to the VespAI weights (.pt). Required with --detector vespai.",
    )
    parser.add_argument(
        "--yolov5-dir",
        type=str,
        default=None,
        help="Path to the local YOLOv5 clone (VespAI submodule). Required with --detector vespai.",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=None,
        help=(
            "ACT/ABSTAIN operating threshold (0-1), see ADR-0004. "
            "Default: 0.45 for rfdetr (ADR-0029), 0.5 for vespai."
        ),
    )
    parser.add_argument(
        "--detector-floor",
        type=float,
        default=None,
        help=(
            "Detector confidence floor (0-1, <= --count-confidence). "
            "Default: min(0.1, --count-confidence). See ADR-0009."
        ),
    )
    parser.add_argument(
        "--count-confidence",
        type=float,
        default=None,
        help=(
            "COUNT point feeding the attack episodes (0-1, <= --confidence), see ADR-0031. "
            "Default: 0.15 for rfdetr, 0.5 for vespai (capped at --confidence)."
        ),
    )
    parser.add_argument(
        "--push",
        choices=["telegram"],
        default=None,
        help=(
            "Also push the attack alert, its summary, the heartbeat and the faults "
            "(ADR-0032, ADR-0033). Telegram reads "
            "ARISTECH_TELEGRAM_TOKEN and ARISTECH_TELEGRAM_CHAT_ID from the environment."
        ),
    )
    args = parser.parse_args(argv)

    if args.logging_config.exists():
        # Logging setup must never crash the app: bad YAML (YAMLError) or a
        # malformed dictConfig (Type/Key/Attribute/Import/Value/OSError) all
        # fall back to a working basic configuration.
        try:
            logging_config = _load_yaml(args.logging_config)
            _ensure_log_dirs(logging_config)
            logging.config.dictConfig(logging_config)
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
    log.info("aristech started, version %s", __version__)

    if args.video is None:
        log.warning("No video source (--video): nothing to analyse.")
        return 0

    try:
        args.episode_rule = _episode_rule(config.get("alert") or {})
        args.health_rule = _health_rule(config.get("health") or {})
    except (TypeError, ValueError):
        log.exception("Invalid alert or health configuration")
        return 2
    return _run_visual_detection(args, log)


def _episode_rule(alert: dict[str, Any]) -> "EpisodeRule":
    """Build the attack episode rule from the `alert` section of the config (ADR-0031)."""
    from datetime import timedelta

    from aristech.application.attack_episode import EpisodeRule

    default = EpisodeRule()
    min_hit_frames = alert.get("min_hit_frames", default.min_hit_frames)
    if isinstance(min_hit_frames, bool) or not isinstance(min_hit_frames, int):
        raise TypeError(f"alert.min_hit_frames must be an integer (got {min_hit_frames!r})")
    return EpisodeRule(
        min_hit_frames=min_hit_frames,
        window=timedelta(seconds=float(alert.get("window_s", default.window.total_seconds()))),
        cooldown=timedelta(
            seconds=float(alert.get("cooldown_s", default.cooldown.total_seconds()))
        ),
    )


def _health_rule(health: dict[str, Any]) -> "HealthRule":
    """Build the heartbeat and fault rate limit from the `health` section (ADR-0033)."""
    from datetime import timedelta

    from aristech.application.health import HealthRule

    default = HealthRule()
    return HealthRule(
        heartbeat=timedelta(
            seconds=float(health.get("heartbeat_s", default.heartbeat.total_seconds()))
        ),
        fault_cooldown=timedelta(
            seconds=float(health.get("fault_cooldown_s", default.fault_cooldown.total_seconds()))
        ),
    )


def _build_notifier(args: argparse.Namespace, log: logging.Logger) -> "Notifier | None":
    """The log sink, wrapped by the push channel when `--push` asks for one (ADR-0032)."""
    from aristech.infrastructure.notify.logging_notifier import LoggingNotifier

    if args.push is None:
        return LoggingNotifier()
    from aristech.infrastructure.notify.telegram_notifier import TelegramNotifier

    try:
        return TelegramNotifier.from_env(LoggingNotifier())
    except ValueError as exc:
        reason = str(exc)
    log.error("Push channel unusable: %s", reason)
    return None


def _model_args_present(args: argparse.Namespace, log: logging.Logger) -> bool:
    if args.detector == "rfdetr":
        if args.checkpoint is None:
            log.error("--detector rfdetr needs --checkpoint.")
            return False
    elif args.weights is None or args.yolov5_dir is None:
        log.error("--detector vespai needs --weights and --yolov5-dir.")
        return False
    return True


def _model_files_ok(args: argparse.Namespace, log: logging.Logger) -> bool:
    """Check the model files exist; warn when the RF-DETR checkpoint is not the one measured
    by ADR-0029, since the default threshold is then not a measured ACT point (ADR-0030)."""
    if args.detector == "rfdetr":
        if not Path(args.checkpoint).is_file():
            log.error("Checkpoint not found: %s", args.checkpoint)
            return False
        if _sha256(Path(args.checkpoint)) != _RFDETR_MEASURED_SHA256:
            log.warning(
                "Checkpoint %s is not the model measured by ADR-0029: "
                "--confidence %s is not a measured ACT point for it.",
                args.checkpoint,
                args.confidence,
            )
        return True
    if not Path(args.weights).is_file():
        log.error("Weights not found: %s", args.weights)
        return False
    if not Path(args.yolov5_dir).is_dir():
        log.error("YOLOv5 directory not found: %s", args.yolov5_dir)
        return False
    return True


def _run_visual_detection(args: argparse.Namespace, log: logging.Logger) -> int:
    """Composition root: build the vision adapters and run `DetectHornetVisual`.
    Imports are local so the base CLI works without the `vision` extra."""
    if not _model_args_present(args, log):
        return 2

    if args.confidence is None:
        args.confidence = _DEFAULT_CONFIDENCE[args.detector]
    if not 0.0 <= args.confidence <= 1.0:
        log.error("--confidence must be in [0, 1] (got %s).", args.confidence)
        return 2

    if args.count_confidence is None:
        args.count_confidence = min(_DEFAULT_COUNT_CONFIDENCE[args.detector], args.confidence)
    if not 0.0 <= args.count_confidence <= args.confidence:
        log.error(
            "--count-confidence must be in [0, --confidence] (got %s, --confidence %s).",
            args.count_confidence,
            args.confidence,
        )
        return 2

    floor = (
        min(_DEFAULT_DETECTOR_FLOOR, args.count_confidence)
        if args.detector_floor is None
        else args.detector_floor
    )
    if not 0.0 <= floor <= args.count_confidence:
        log.error(
            "--detector-floor must be in [0, --count-confidence] (got %s, --count-confidence %s).",
            floor,
            args.count_confidence,
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

    if not _model_files_ok(args, log):
        return 2
    notifier = _build_notifier(args, log)
    if notifier is None:
        return 2
    log.info(
        "Detector %s, ACT threshold %s, COUNT threshold %s, detector floor %s.",
        args.detector,
        args.confidence,
        args.count_confidence,
        floor,
    )

    from aristech.application.health import HealthMonitor
    from aristech.application.use_cases import (
        DetectHornetVisual,
        DetectHornetVisualConfig,
    )
    from aristech.infrastructure.capture.system_clock import SystemClock
    from aristech.infrastructure.vision.opencv_video_source import OpenCVVideoSource

    detector = _TimedDetector(_build_detector(args, floor))
    use_case = DetectHornetVisual(
        video=OpenCVVideoSource(source),
        detector=detector,
        notifier=notifier,
        config=DetectHornetVisualConfig(
            confidence_threshold=args.confidence,
            count_threshold=args.count_confidence,
            episode_rule=args.episode_rule,
            live_source=isinstance(source, int),
        ),
        health=HealthMonitor(args.health_rule, SystemClock()),
    )
    start = time.perf_counter()
    try:
        result = use_case.run()
    finally:
        _log_timing(log, detector.latencies, time.perf_counter() - start)
    log.info(
        "Analysis done: %d threat(s), %d abstention(s) below the threshold, %d attack episode(s).",
        result.threats,
        result.abstentions,
        result.episodes,
    )
    return 0


def _build_detector(args: argparse.Namespace, floor: float) -> "HornetDetector":
    """Build the chosen detector at the floor; imports stay lazy (optional extras)."""
    if args.detector == "rfdetr":
        from aristech.infrastructure.vision.rfdetr_detector import RFDETRDetector

        return RFDETRDetector(checkpoint_path=args.checkpoint, confidence=floor)
    from aristech.infrastructure.vision.vespai_detector import VespAIDetector

    return VespAIDetector(weights_path=args.weights, yolov5_dir=args.yolov5_dir, confidence=floor)


if __name__ == "__main__":
    sys.exit(main())
