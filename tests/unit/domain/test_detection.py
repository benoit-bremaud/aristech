from datetime import datetime

import pytest

from aristech.domain import BoundingBox, Detection, Species


def _bbox() -> BoundingBox:
    return BoundingBox(x=0.0, y=0.0, width=10.0, height=10.0)


def test_detection_marks_velutina_as_threat():
    det = Detection(
        species=Species.VESPA_VELUTINA,
        bbox=_bbox(),
        confidence=0.9,
        timestamp=datetime(2026, 5, 19),
    )
    assert det.is_hornet()
    assert det.is_threat()


def test_detection_crabro_is_hornet_but_not_threat():
    det = Detection(
        species=Species.VESPA_CRABRO,
        bbox=_bbox(),
        confidence=0.8,
        timestamp=datetime(2026, 5, 19),
    )
    assert det.is_hornet()
    assert not det.is_threat()


def test_detection_rejects_invalid_confidence():
    with pytest.raises(ValueError):
        Detection(
            species=Species.VESPA_VELUTINA,
            bbox=_bbox(),
            confidence=1.5,
            timestamp=datetime(2026, 5, 19),
        )


def test_bounding_box_rejects_negative_dimensions():
    with pytest.raises(ValueError):
        BoundingBox(x=0.0, y=0.0, width=-1.0, height=1.0)


def test_bounding_box_center_and_area():
    bbox = BoundingBox(x=0.0, y=0.0, width=4.0, height=2.0)
    assert bbox.area == 8.0
    assert bbox.center.x == 2.0
    assert bbox.center.y == 1.0
