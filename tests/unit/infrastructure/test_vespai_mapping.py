from datetime import datetime

from aristech.domain import Species
from aristech.infrastructure.vision.vespai_detector import detection_from_box

TS = datetime(2026, 5, 21)


def test_velutina_maps_to_threat_and_bbox_from_xyxy():
    det = detection_from_box("Vespa velutina", 0.9, 10, 20, 30, 60, TS)
    assert det.species is Species.VESPA_VELUTINA
    assert det.is_threat()
    assert (det.bbox.x, det.bbox.y, det.bbox.width, det.bbox.height) == (10, 20, 20, 40)
    assert det.confidence == 0.9
    assert det.timestamp == TS


def test_crabro_is_detected_but_not_a_threat():
    det = detection_from_box("Vespa crabro", 0.95, 0, 0, 10, 10, TS)
    assert det.species is Species.VESPA_CRABRO
    assert det.is_hornet()
    assert not det.is_threat()


def test_unknown_class_name_maps_to_unknown():
    # VespAI has no bee class; anything outside the two hornet species
    # (or a future fine-tuned label) must not be treated as a target.
    det = detection_from_box("Apis mellifera", 0.99, 0, 0, 5, 5, TS)
    assert det.species is Species.UNKNOWN
    assert not det.is_threat()
