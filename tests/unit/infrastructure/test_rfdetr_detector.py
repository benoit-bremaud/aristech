"""RF-DETR adapter: class mapping and the lazy load, with a fake `rfdetr` module (no torch)."""

import sys
import types
from datetime import UTC, datetime

import numpy as np
import pytest

from aristech.domain import Species, VideoFrame
from aristech.infrastructure.vision.rfdetr_detector import RFDETRDetector, detections_from_arrays

_TS = datetime(2026, 10, 23, tzinfo=UTC)
_NAMES = ["vespa_velutina", "vespa_crabro", "apis_mellifera", "other"]


@pytest.mark.parametrize(
    ("class_id", "species"),
    [
        (0, Species.VESPA_VELUTINA),
        (1, Species.VESPA_CRABRO),
        (2, Species.APIS_MELLIFERA),
        (3, Species.UNKNOWN),
        (9, Species.UNKNOWN),
    ],
)
def test_class_ids_map_through_the_model_class_names(class_id: int, species: Species) -> None:
    [detection] = detections_from_arrays([[10, 20, 40, 60]], [0.9], [class_id], _NAMES, _TS)
    assert detection.species is species
    assert (detection.bbox.x, detection.bbox.y) == (10.0, 20.0)
    assert (detection.bbox.width, detection.bbox.height) == (30.0, 40.0)
    assert detection.confidence == pytest.approx(0.9)


class _FakeModel:
    class_names = _NAMES

    def __init__(self) -> None:
        self.seen: list[tuple[np.ndarray, float]] = []

    def predict(self, image: np.ndarray, threshold: float, include_source_image: bool) -> object:
        self.seen.append((image, threshold))
        return types.SimpleNamespace(
            xyxy=np.array([[1.0, 2.0, 3.0, 4.0]]),
            confidence=np.array([0.7]),
            class_id=np.array([1]),
        )


def test_detect_loads_once_converts_bgr_and_maps(monkeypatch: pytest.MonkeyPatch) -> None:
    model = _FakeModel()
    loads: list[str] = []

    def from_checkpoint(path: str) -> _FakeModel:
        loads.append(path)
        return model

    monkeypatch.setitem(
        sys.modules, "rfdetr", types.SimpleNamespace(from_checkpoint=from_checkpoint)
    )
    pixels = np.zeros((2, 2, 3), dtype=np.uint8)
    pixels[..., 0] = 255  # blue in BGR
    frame = VideoFrame(pixels=pixels, width=2, height=2, timestamp=_TS)
    detector = RFDETRDetector("best.pth", confidence=0.3)

    first = detector.detect(frame)
    detector.detect(frame)

    assert loads == ["best.pth"]
    image, threshold = model.seen[0]
    assert threshold == 0.3
    assert image[0, 0, 2] == 255
    assert image[0, 0, 0] == 0
    assert first[0].species is Species.VESPA_CRABRO
