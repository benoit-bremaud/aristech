"""`HornetDetector` adapter for a fine-tuned RF-DETR checkpoint (ADR-0022, ADR-0024).

`rfdetr` (Apache-2.0, extra `train`) is imported lazily so the core package installs without
it. The checkpoint is git-ignored and loaded from a path; only trusted, locally trained files
are loaded; `rfdetr.from_checkpoint` keeps its safe (weights-only) loading by default. The
model's class names (the canonical ones of ADR-0018) map to the `Species` of the same value;
any other name, `other` included, maps to `UNKNOWN`.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any

from aristech.domain import BoundingBox, Detection, Species, VideoFrame


def detections_from_arrays(
    xyxy: Sequence[Sequence[float]],
    confidences: Sequence[float],
    class_ids: Sequence[int],
    class_names: Sequence[str],
    timestamp: datetime,
) -> list[Detection]:
    """Build domain detections from RF-DETR outputs. Pure: unit-tested without torch.

    Boxes go from corner form (x0, y0, x1, y1) to x / y / width / height. A class id outside
    `class_names` maps to `UNKNOWN`; inputs of different lengths raise `ValueError`.
    """
    detections = []
    for (x0, y0, x1, y1), confidence, class_id in zip(xyxy, confidences, class_ids, strict=True):
        index = int(class_id)
        name = class_names[index] if 0 <= index < len(class_names) else ""
        species = Species(name) if name in Species._value2member_map_ else Species.UNKNOWN
        detections.append(
            Detection(
                species=species,
                bbox=BoundingBox(
                    x=float(x0), y=float(y0), width=float(x1 - x0), height=float(y1 - y0)
                ),
                confidence=float(confidence),
                timestamp=timestamp,
            )
        )
    return detections


class RFDETRDetector:
    """`HornetDetector` running a fine-tuned RF-DETR checkpoint, loaded on first use."""

    def __init__(self, checkpoint_path: str, confidence: float = 0.5) -> None:
        """`confidence` is the model's own floor; pass the lowest threshold you will score.

        Nothing is loaded here: a bad path fails on the first `detect` call.
        """
        self._checkpoint_path = checkpoint_path
        self._confidence = confidence
        self._model: Any | None = None

    def _load(self) -> Any:
        if self._model is None:
            from rfdetr import from_checkpoint

            self._model = from_checkpoint(self._checkpoint_path)
        return self._model

    def detect(self, frame: VideoFrame) -> Sequence[Detection]:
        """Run the model on the BGR frame (converted to RGB) and map each box."""
        model = self._load()
        rgb = frame.pixels[..., ::-1].copy()  # numpy BGR array -> RGB
        result = model.predict(rgb, threshold=self._confidence, include_source_image=False)
        return detections_from_arrays(
            result.xyxy.tolist(),
            result.confidence.tolist(),
            result.class_id.tolist(),
            model.class_names,
            frame.timestamp,
        )
