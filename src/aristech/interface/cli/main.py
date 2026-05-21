import argparse
import logging
import logging.config
import sys
from pathlib import Path
from typing import Any, cast

import yaml


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} doit contenir un mapping YAML, pas {type(data).__name__}")
    return cast(dict[str, Any], data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aristech")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/config.yaml"),
        help="Chemin du fichier de configuration applicatif.",
    )
    parser.add_argument(
        "--logging-config",
        type=Path,
        default=Path("config/logging.yaml"),
        help="Chemin du fichier de configuration logging.",
    )
    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="Source vidéo (fichier ou index caméra) à analyser. Requiert l'extra 'vision'.",
    )
    parser.add_argument(
        "--weights",
        type=str,
        default=None,
        help="Chemin des poids VespAI (.pt). Requis avec --video.",
    )
    parser.add_argument(
        "--yolov5-dir",
        type=str,
        default=None,
        help="Chemin du clone local YOLOv5 (sous-module VespAI). Requis avec --video.",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.5,
        help="Seuil de confiance des détections (0-1).",
    )
    args = parser.parse_args(argv)

    if args.logging_config.exists():
        try:
            logging.config.dictConfig(_load_yaml(args.logging_config))
        except (ValueError, OSError) as exc:
            logging.basicConfig(level=logging.INFO)
            logging.getLogger("aristech").warning(
                "Config logging inutilisable (%s) — repli sur basicConfig.", exc
            )
    else:
        logging.basicConfig(level=logging.INFO)

    log = logging.getLogger("aristech")

    if not args.config.exists():
        log.error("Configuration introuvable : %s", args.config)
        return 2

    config = _load_yaml(args.config)
    log.info("Aristech démarré — version %s", config.get("app", {}).get("version", "?"))

    if args.video is None:
        log.warning("Aucune source vidéo (--video) — rien à analyser.")
        return 0

    return _run_visual_detection(args, log)


def _run_visual_detection(args: argparse.Namespace, log: logging.Logger) -> int:
    """Composition root : instancie les adaptateurs vision et lance le use
    case `DetectHornetVisual`. Les imports sont locaux pour que le CLI de
    base fonctionne sans l'extra `vision`."""
    if args.weights is None or args.yolov5_dir is None:
        log.error("--video requiert --weights et --yolov5-dir.")
        return 2

    from aristech.application.use_cases import (
        DetectHornetVisual,
        DetectHornetVisualConfig,
    )
    from aristech.infrastructure.notify.logging_notifier import LoggingNotifier
    from aristech.infrastructure.vision.opencv_video_source import OpenCVVideoSource
    from aristech.infrastructure.vision.vespai_detector import VespAIDetector

    source: str | int = int(args.video) if args.video.isdigit() else args.video
    use_case = DetectHornetVisual(
        video=OpenCVVideoSource(source),
        detector=VespAIDetector(
            weights_path=args.weights,
            yolov5_dir=args.yolov5_dir,
            confidence=args.confidence,
        ),
        notifier=LoggingNotifier(),
        config=DetectHornetVisualConfig(confidence_threshold=args.confidence),
    )
    accepted = use_case.run()
    log.info("Analyse terminée — %d menace(s) au-dessus du seuil.", len(accepted))
    return 0


if __name__ == "__main__":
    sys.exit(main())
