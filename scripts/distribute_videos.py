"""CLI : répartit les vidéos entre TRAIN/VALIDATION/TEST_FOLDER.

Lit les chemins depuis le fichier `.env` (cf. `.env.example`).
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

from aristech.training.distribute import distribute_files

VIDEO_EXTENSIONS = (".mp4", ".mov", ".avi", ".mkv", ".webm")


def main() -> int:
    load_dotenv()

    source = os.getenv("SOURCE_FOLDER")
    train = os.getenv("TRAIN_FOLDER")
    validation = os.getenv("VALIDATION_FOLDER")
    test = os.getenv("TEST_FOLDER")

    if not all([source, train, validation, test]):
        print("SOURCE_FOLDER / TRAIN_FOLDER / VALIDATION_FOLDER / TEST_FOLDER manquant(s) dans .env")
        return 1

    counts = distribute_files(source, train, validation, test, extensions=VIDEO_EXTENSIONS)  # type: ignore[arg-type]
    print(f"Vidéos réparties : {counts[0]} train, {counts[1]} validation, {counts[2]} test.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
