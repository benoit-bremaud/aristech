from datetime import datetime
from pathlib import Path

import pytest

from aristech.domain import BoundingBox, Detection, Species, VideoFrame
from aristech.evaluation import evaluate_on_dataset

TS = datetime(2026, 5, 23)
CLASS_MAP = {0: Species.VESPA_CRABRO, 1: Species.VESPA_VELUTINA}


def _fake_reader(path: Path) -> tuple[None, int, int]:
    # 100x100; pixels unused by the fake detector.
    return None, 100, 100


class _FixedDetector:
    def __init__(self, detections: list[Detection]) -> None:
        self._detections = detections

    def detect(self, frame: VideoFrame) -> list[Detection]:
        return self._detections


def _det(species: Species, conf: float, box: BoundingBox) -> Detection:
    return Detection(species=species, bbox=box, confidence=conf, timestamp=TS)


def _make_split(base: Path, split: str, items: list[tuple[str, list[str]]]) -> None:
    images = base / split / "images"
    labels = base / split / "labels"
    images.mkdir(parents=True)
    labels.mkdir(parents=True)
    for stem, lines in items:
        (images / f"{stem}.jpg").write_bytes(b"")
        (labels / f"{stem}.txt").write_text("\n".join(lines), encoding="utf-8")


def test_perfect_detection_scores_one(tmp_path):
    # GT velutina box: class 1, cx=cy=0.5 w=h=0.2 on 100x100 → (40,40,20,20)
    _make_split(tmp_path, "test", [("img1", ["1 0.5 0.5 0.2 0.2"])])
    detector = _FixedDetector([_det(Species.VESPA_VELUTINA, 0.9, BoundingBox(40, 40, 20, 20))])
    report = evaluate_on_dataset(detector, tmp_path, CLASS_MAP, image_reader=_fake_reader)
    m = report.class_metrics(Species.VESPA_VELUTINA)
    assert (m.tp, m.fp, m.fn) == (1, 0, 0)


def test_unlabelled_image_yields_false_positive(tmp_path):
    _make_split(tmp_path, "test", [("img1", [])])  # empty label = background
    detector = _FixedDetector([_det(Species.VESPA_VELUTINA, 0.9, BoundingBox(40, 40, 20, 20))])
    report = evaluate_on_dataset(detector, tmp_path, CLASS_MAP, image_reader=_fake_reader)
    assert report.class_metrics(Species.VESPA_VELUTINA).fp == 1


def test_confidence_threshold_filters_predictions(tmp_path):
    _make_split(tmp_path, "test", [("img1", ["1 0.5 0.5 0.2 0.2"])])
    detector = _FixedDetector([_det(Species.VESPA_VELUTINA, 0.3, BoundingBox(40, 40, 20, 20))])
    report = evaluate_on_dataset(
        detector, tmp_path, CLASS_MAP, image_reader=_fake_reader, confidence_threshold=0.5
    )
    # low-confidence prediction dropped → the GT is missed.
    assert report.class_metrics(Species.VESPA_VELUTINA).fn == 1


def test_aggregates_multiple_splits(tmp_path):
    _make_split(tmp_path, "valid", [("a", ["1 0.5 0.5 0.2 0.2"])])
    _make_split(tmp_path, "test", [("b", ["1 0.5 0.5 0.2 0.2"])])
    detector = _FixedDetector([_det(Species.VESPA_VELUTINA, 0.9, BoundingBox(40, 40, 20, 20))])
    report = evaluate_on_dataset(
        detector, tmp_path, CLASS_MAP, splits=("valid", "test"), image_reader=_fake_reader
    )
    assert report.class_metrics(Species.VESPA_VELUTINA).tp == 2


def test_missing_label_file_treated_as_negative(tmp_path):
    # Image with no matching .txt at all → negative image, a detection is a FP.
    _make_split(tmp_path, "test", [])
    (tmp_path / "test" / "images" / "img1.jpg").write_bytes(b"")
    detector = _FixedDetector([_det(Species.VESPA_VELUTINA, 0.9, BoundingBox(40, 40, 20, 20))])
    report = evaluate_on_dataset(detector, tmp_path, CLASS_MAP, image_reader=_fake_reader)
    assert report.class_metrics(Species.VESPA_VELUTINA).fp == 1


def test_non_image_files_are_skipped(tmp_path):
    _make_split(tmp_path, "test", [("img1", ["1 0.5 0.5 0.2 0.2"])])
    (tmp_path / "test" / "images" / "notes.txt").write_text("ignore me", encoding="utf-8")
    detector = _FixedDetector([_det(Species.VESPA_VELUTINA, 0.9, BoundingBox(40, 40, 20, 20))])
    report = evaluate_on_dataset(detector, tmp_path, CLASS_MAP, image_reader=_fake_reader)
    # Only the one real image is scored; notes.txt never reaches the reader.
    assert report.class_metrics(Species.VESPA_VELUTINA).tp == 1


def test_missing_split_raises(tmp_path):
    _make_split(tmp_path, "valid", [("a", ["1 0.5 0.5 0.2 0.2"])])
    detector = _FixedDetector([])
    with pytest.raises(FileNotFoundError):
        evaluate_on_dataset(
            detector, tmp_path, CLASS_MAP, splits=("test",), image_reader=_fake_reader
        )
