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
    args = parser.parse_args(argv)

    if args.logging_config.exists():
        logging.config.dictConfig(_load_yaml(args.logging_config))
    else:
        logging.basicConfig(level=logging.INFO)

    log = logging.getLogger("aristech")

    if not args.config.exists():
        log.error("Configuration introuvable : %s", args.config)
        return 2

    config = _load_yaml(args.config)
    log.info("Aristech démarré — version %s", config.get("app", {}).get("version", "?"))
    log.warning("Aucun use case branché — composition root à compléter.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
