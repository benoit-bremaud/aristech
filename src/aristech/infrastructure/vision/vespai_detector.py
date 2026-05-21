"""`HornetDetector` adapter wrapping the VespAI YOLOv5 model.

`torch` and the YOLOv5 code are imported lazily so the core package installs
without the `vision` extra. VespAI's weights are CC BY-NC-SA (non-commercial)
and the YOLOv5 code is AGPL-3.0 — both are loaded at runtime from a path you
supply; neither is bundled with aristech.

The model's output classes are exactly ``Vespa velutina`` and ``Vespa
crabro`` (M0 finding — no bee class); anything else maps to ``UNKNOWN``.
Bees are negatives (no detection), which still satisfies the legal floor.
"""

import logging
import threading
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from aristech.domain import BoundingBox, Detection, Species, VideoFrame

_log = logging.getLogger("aristech.vision")

# Loading the YOLOv5 checkpoint requires temporarily relaxing torch's
# weights_only default. That mutates the global `torch.load`, so serialise
# it behind a lock to keep concurrent detector loads safe.
_LOAD_LOCK = threading.Lock()

# VespAI YOLOv5 class name → domain Species.
_SPECIES_BY_NAME: dict[str, Species] = {
    "Vespa velutina": Species.VESPA_VELUTINA,
    "Vespa crabro": Species.VESPA_CRABRO,
}


def detection_from_box(
    name: str,
    confidence: float,
    xmin: float,
    ymin: float,
    xmax: float,
    ymax: float,
    timestamp: datetime,
) -> Detection:
    """Build a domain `Detection` from one VespAI box. Pure — unit-tested
    without torch. An unknown class name maps to `Species.UNKNOWN`."""
    return Detection(
        species=_SPECIES_BY_NAME.get(name, Species.UNKNOWN),
        bbox=BoundingBox(
            x=float(xmin),
            y=float(ymin),
            width=float(xmax - xmin),
            height=float(ymax - ymin),
        ),
        confidence=float(confidence),
        timestamp=timestamp,
    )


class VespAIDetector:
    def __init__(
        self,
        weights_path: str,
        yolov5_dir: str,
        confidence: float = 0.5,
    ) -> None:
        """`weights_path`: VespAI `.pt` weights. `yolov5_dir`: local clone
        of the YOLOv5 repo (the VespAI submodule). `confidence`: detector
        threshold passed to YOLOv5."""
        self._weights_path = weights_path
        self._yolov5_dir = yolov5_dir
        self._confidence = confidence
        self._model: Any | None = None

    def _load(self) -> Any:
        if self._model is None:
            import torch

            # torch>=2.6 defaults weights_only=True, which rejects the YOLOv5
            # checkpoint. Relaxing it re-enables pickle deserialisation, which
            # can execute arbitrary code from a malicious .pt — only trusted,
            # operator-supplied weights must be used here.
            _log.warning(
                "Loading weights with weights_only=False (pickle): %s — only "
                "use trusted .pt files.",
                self._weights_path,
            )
            with _LOAD_LOCK:
                original_load = torch.load

                def _trusted_load(*args: Any, **kwargs: Any) -> Any:
                    kwargs.setdefault("weights_only", False)
                    return original_load(*args, **kwargs)

                torch.load = _trusted_load
                try:
                    model = torch.hub.load(
                        self._yolov5_dir,
                        "custom",
                        path=self._weights_path,
                        source="local",
                        _verbose=False,
                    )
                finally:
                    torch.load = original_load
            model.conf = self._confidence
            self._model = model
        return self._model

    def detect(self, frame: VideoFrame) -> Sequence[Detection]:
        import cv2

        model = self._load()
        rgb = cv2.cvtColor(frame.pixels, cv2.COLOR_BGR2RGB)
        results = model(rgb)
        return [
            detection_from_box(
                row.name,
                row.confidence,
                row.xmin,
                row.ymin,
                row.xmax,
                row.ymax,
                frame.timestamp,
            )
            for row in results.pandas().xyxy[0].itertuples()
        ]
