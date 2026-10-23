"""`HornetDetector` adapter for a fine-tuned RF-DETR checkpoint (ADR-0022, ADR-0024).

`rfdetr` (Apache-2.0, extra `train`) is imported lazily so the core package installs without
it. The checkpoint is git-ignored and loaded from a path; only trusted, locally trained files
are loaded. The model's class names (the canonical ones of ADR-0018) map to `Species`; any
other name maps to `UNKNOWN`.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Any

from aristech.domain import BoundingBox, Detection, Species, VideoFrame

_SPECIES_BY_NAME: dict[str, Species] = {
    "vespa_velutina": Species.VESPA_VELUTINA,
    "vespa_crabro": Species.VESPA_CRABRO,
    "apis_mellifera": Species.APIS_MELLIFERA,
}


def detections_from_arrays(
    xyxy: Sequence[Sequence[float]],
    confidences: Sequence[float],
    class_ids: Sequence[int],
    class_names: Sequence[str],
    timestamp: datetime,
) -> list[Detection]:
    """Build domain detections from RF-DETR outputs. Pure: unit-tested without torch."""
    detections = []
    for (x0, y0, x1, y1), confidence, class_id in zip(xyxy, confidences, class_ids, strict=True):
        index = int(class_id)
        name = class_names[index] if 0 <= index < len(class_names) else ""
        detections.append(
            Detection(
                species=_SPECIES_BY_NAME.get(name, Species.UNKNOWN),
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
        """`confidence` is the model's own floor; pass the lowest threshold you will score."""
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
