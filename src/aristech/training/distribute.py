"""Répartition aléatoire des fichiers source entre train/validation/test.

Pure fonction sans dotenv ni I/O parasite : les variables d'environnement
sont résolues côté `scripts/`, pas ici. Cela permet de tester la fonction
sans dépendre du shell.
"""

from __future__ import annotations

import random
import shutil
from collections.abc import Sequence
from pathlib import Path


def distribute_files(
    source_folder: Path | str,
    train_folder: Path | str,
    validation_folder: Path | str,
    test_folder: Path | str,
    *,
    train_ratio: float = 0.7,
    validation_ratio: float = 0.2,
    extensions: Sequence[str] | None = None,
    seed: int | None = None,
) -> tuple[int, int, int]:
    """Déplace les fichiers de `source_folder` vers train/val/test.

    Retourne `(train_count, validation_count, test_count)`.

    `train_ratio + validation_ratio` ≤ 1.0 ; le reste va dans test.
    Si `extensions` est fourni (ex. `(".jpg", ".png")`), filtre les
    fichiers correspondants. `seed` permet de rendre le tirage
    reproductible.
    """

    if train_ratio + validation_ratio > 1.0:
        raise ValueError("train_ratio + validation_ratio must be ≤ 1.0")

    source = Path(source_folder)
    train = Path(train_folder)
    validation = Path(validation_folder)
    test = Path(test_folder)

    for d in (train, validation, test):
        d.mkdir(parents=True, exist_ok=True)

    all_files = [
        p
        for p in source.iterdir()
        if p.is_file() and (extensions is None or p.suffix.lower() in extensions)
    ]

    if not all_files:
        return 0, 0, 0

    rng = random.Random(seed)
    rng.shuffle(all_files)

    total = len(all_files)
    train_count = int(train_ratio * total)
    validation_count = int(validation_ratio * total)
    test_count = total - train_count - validation_count

    for idx, src in enumerate(all_files):
        if idx < train_count:
            dest = train / src.name
        elif idx < train_count + validation_count:
            dest = validation / src.name
        else:
            dest = test / src.name
        shutil.move(str(src), str(dest))

    return train_count, validation_count, test_count
