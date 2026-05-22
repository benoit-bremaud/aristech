"""Parse YOLO-format detection labels into domain `Annotation`s.

YOLO is the de-facto label format for the datasets aristech will evaluate
against (VespAI's, the Roboflow sets). Each label line is::

    <class_id> <cx> <cy> <w> <h>

with the box centre and size **normalised to [0, 1]**. This module converts
those into pixel-space `Annotation`s (matching the detector's pixel boxes),
so the result can be fed straight to `evaluate`. Pure — no file/image I/O —
so it is unit-tested in CI; reading files and image dimensions is the
caller's job (the runner, which arrives with a real dataset).
"""

from collections.abc import Mapping, Sequence

from aristech.domain import BoundingBox, Species
from aristech.evaluation.metrics import Annotation


def parse_yolo_labels(
    lines: Sequence[str],
    image_width: int,
    image_height: int,
    class_map: Mapping[int, Species],
) -> list[Annotation]:
    """Parse YOLO label `lines` into pixel-space `Annotation`s.

    `class_map` maps the integer class id to a `Species`; an id absent from
    the map becomes `Species.UNKNOWN`. Blank lines are ignored. Raises
    `ValueError` on a malformed line or out-of-range normalised value.
    """
    if image_width <= 0 or image_height <= 0:
        raise ValueError(f"image size must be positive, got {image_width}x{image_height}")

    annotations: list[Annotation] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 5:
            raise ValueError(f"YOLO label needs 5 fields, got {len(parts)}: {raw!r}")
        class_id = int(parts[0])
        cx, cy, w, h = (float(p) for p in parts[1:])
        if not all(0.0 <= v <= 1.0 for v in (cx, cy, w, h)):
            raise ValueError(f"YOLO values must be normalised in [0, 1]: {raw!r}")
        annotations.append(
            Annotation(
                species=class_map.get(class_id, Species.UNKNOWN),
                bbox=BoundingBox(
                    x=(cx - w / 2) * image_width,
                    y=(cy - h / 2) * image_height,
                    width=w * image_width,
                    height=h * image_height,
                ),
            )
        )
    return annotations
