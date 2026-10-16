"""CLI : répartit les vidéos entre VIDEO_TRAIN/VIDEO_VALIDATION/VIDEO_TEST_FOLDER.

Lit les chemins depuis le fichier `.env` (cf. `.env.example`). Utilise des
variables dédiées (`VIDEO_*`) pour qu'images et vidéos puissent coexister
dans le même `.env` sans se piétiner.
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

from aristech.datasets.distribute import distribute_files

VIDEO_EXTENSIONS = (".mp4", ".mov", ".avi", ".mkv", ".webm")


def main() -> int:
    load_dotenv()

    source = os.getenv("VIDEO_SOURCE_FOLDER")
    train = os.getenv("VIDEO_TRAIN_FOLDER")
    validation = os.getenv("VIDEO_VALIDATION_FOLDER")
    test = os.getenv("VIDEO_TEST_FOLDER")

    if not all([source, train, validation, test]):
        print(
            "VIDEO_SOURCE_FOLDER / VIDEO_TRAIN_FOLDER / "
            "VIDEO_VALIDATION_FOLDER / VIDEO_TEST_FOLDER manquant(s) dans .env"
        )
        return 1

    counts = distribute_files(source, train, validation, test, extensions=VIDEO_EXTENSIONS)  # type: ignore[arg-type]
    print(f"Vidéos réparties : {counts[0]} train, {counts[1]} validation, {counts[2]} test.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
