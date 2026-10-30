"""Integration test for the VespAI detector adapter.

Skipped unless `torch` + `cv2` are installed AND the VespAI assets are
pointed to via environment variables (the weights are CC BY-NC-SA and not
bundled, so paths must be supplied explicitly):

    VESPAI_WEIGHTS       path to a VespAI .pt weights file
    VESPAI_YOLOV5_DIR    path to a local YOLOv5 clone (the VespAI submodule)
    VESPAI_SAMPLE_IMAGE  path to an image containing a Vespa velutina
"""

import os
from datetime import UTC, datetime

import pytest

pytestmark = pytest.mark.integration


def test_detects_velutina_on_sample_image():
    cv2 = pytest.importorskip("cv2")
    pytest.importorskip("torch")
    pytest.importorskip("pandas")

    weights = os.environ.get("VESPAI_WEIGHTS")
    yolov5_dir = os.environ.get("VESPAI_YOLOV5_DIR")
    sample = os.environ.get("VESPAI_SAMPLE_IMAGE")
    if not (weights and yolov5_dir and sample):
        pytest.skip("set VESPAI_WEIGHTS, VESPAI_YOLOV5_DIR, VESPAI_SAMPLE_IMAGE to run")

    from aristech.domain import Species, VideoFrame
    from aristech.infrastructure.vision.vespai_detector import VespAIDetector

    image = cv2.imread(sample)
    assert image is not None, f"could not read {sample}"
    frame = VideoFrame(
        pixels=image,
        width=int(image.shape[1]),
        height=int(image.shape[0]),
        timestamp=datetime.now(UTC),
    )

    detections = VespAIDetector(weights, yolov5_dir, confidence=0.5).detect(frame)
    assert any(d.species is Species.VESPA_VELUTINA for d in detections)
    assert all(0.0 <= d.confidence <= 1.0 for d in detections)
