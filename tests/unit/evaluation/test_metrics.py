from datetime import datetime

import pytest

from aristech.domain import BoundingBox, Detection, Species
from aristech.evaluation import Annotation, evaluate, iou

TS = datetime(2026, 5, 22)


def _box(x, y, w=10.0, h=10.0):
    return BoundingBox(x=x, y=y, width=w, height=h)


def _pred(species, conf, box):
    return Detection(species=species, bbox=box, confidence=conf, timestamp=TS)


def _gt(species, box):
    return Annotation(species=species, bbox=box)


def test_iou_identical_disjoint_partial():
    assert iou(_box(0, 0), _box(0, 0)) == 1.0
    assert iou(_box(0, 0), _box(100, 100)) == 0.0
    assert iou(_box(0, 0), _box(5, 0)) == pytest.approx(1 / 3)


def test_perfect_detection_gives_precision_recall_one():
    pred = _pred(Species.VESPA_VELUTINA, 0.9, _box(0, 0))
    gt = _gt(Species.VESPA_VELUTINA, _box(0, 0))
    report = evaluate([([pred], [gt])])
    m = report.class_metrics(Species.VESPA_VELUTINA)
    assert (m.tp, m.fp, m.fn) == (1, 0, 0)
    assert m.precision == 1.0 and m.recall == 1.0 and m.f1 == 1.0


def test_false_positive_when_no_ground_truth():
    pred = _pred(Species.VESPA_VELUTINA, 0.9, _box(0, 0))
    report = evaluate([([pred], [])])
    m = report.class_metrics(Species.VESPA_VELUTINA)
    assert (m.tp, m.fp, m.fn) == (0, 1, 0)


def test_miss_when_no_prediction():
    gt = _gt(Species.VESPA_VELUTINA, _box(0, 0))
    report = evaluate([([], [gt])])
    m = report.class_metrics(Species.VESPA_VELUTINA)
    assert (m.tp, m.fp, m.fn) == (0, 0, 1)


def test_confidence_threshold_drops_low_predictions():
    low = _pred(Species.VESPA_VELUTINA, 0.3, _box(0, 0))
    gt = _gt(Species.VESPA_VELUTINA, _box(0, 0))
    report = evaluate([([low], [gt])], confidence_threshold=0.5)
    m = report.class_metrics(Species.VESPA_VELUTINA)
    assert (m.tp, m.fp, m.fn) == (0, 0, 1)  # dropped → the GT is missed


def test_no_iou_overlap_is_fp_plus_fn_not_a_match():
    pred = _pred(Species.VESPA_VELUTINA, 0.9, _box(0, 0))
    gt = _gt(Species.VESPA_VELUTINA, _box(100, 100))
    report = evaluate([([pred], [gt])])
    m = report.class_metrics(Species.VESPA_VELUTINA)
    assert (m.tp, m.fp, m.fn) == (0, 1, 1)


def test_species_confusion_velutina_predicted_as_crabro():
    pred = _pred(Species.VESPA_CRABRO, 0.9, _box(0, 0))
    gt = _gt(Species.VESPA_VELUTINA, _box(0, 0))
    report = evaluate([([pred], [gt])])
    assert report.confusion[("vespa_velutina", "vespa_crabro")] == 1
    # velutina: matched to a wrong-class pred → a miss
    assert report.class_metrics(Species.VESPA_VELUTINA).fn == 1
    # crabro: predicted where there was none of its class → a false positive
    assert report.class_metrics(Species.VESPA_CRABRO).fp == 1


def test_bee_predicted_as_hornet_is_a_velutina_false_positive():
    # The legal-floor critical case: a bee location predicted as a hornet.
    pred = _pred(Species.VESPA_VELUTINA, 0.95, _box(0, 0))
    gt = _gt(Species.APIS_MELLIFERA, _box(0, 0))
    report = evaluate([([pred], [gt])])
    assert report.confusion[("apis_mellifera", "vespa_velutina")] == 1
    assert report.class_metrics(Species.VESPA_VELUTINA).fp == 1
    assert report.class_metrics(Species.APIS_MELLIFERA).fn == 1


def test_format_text_lists_classes():
    pred = _pred(Species.VESPA_VELUTINA, 0.9, _box(0, 0))
    gt = _gt(Species.VESPA_VELUTINA, _box(0, 0))
    text = evaluate([([pred], [gt])]).format_text()
    assert "vespa_velutina" in text
    assert "P" in text and "R" in text and "F1" in text
