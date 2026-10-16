"""CLI: split the images into TRAIN/VALIDATION/TEST_FOLDER.

Reads the paths from `.env` (see `.env.example`).
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

from aristech.datasets.distribute import distribute_files

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


def main() -> int:
    load_dotenv()

    source = os.getenv("SOURCE_FOLDER")
    train = os.getenv("TRAIN_FOLDER")
    validation = os.getenv("VALIDATION_FOLDER")
    test = os.getenv("TEST_FOLDER")

    if not all([source, train, validation, test]):
        print("SOURCE_FOLDER / TRAIN_FOLDER / VALIDATION_FOLDER / TEST_FOLDER missing from .env")
        return 1

    counts = distribute_files(source, train, validation, test, extensions=IMAGE_EXTENSIONS)  # type: ignore[arg-type]
    print(f"Images split: {counts[0]} train, {counts[1]} validation, {counts[2]} test.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
