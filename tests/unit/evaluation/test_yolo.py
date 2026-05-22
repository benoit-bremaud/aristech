import pytest

from aristech.domain import Species
from aristech.evaluation import parse_yolo_labels

# VespAI ordering: 0 = crabro, 1 = velutina.
CLASS_MAP = {0: Species.VESPA_CRABRO, 1: Species.VESPA_VELUTINA}


def test_parses_centre_normalised_box_to_pixels():
    # cx=0.5, cy=0.5, w=0.2, h=0.4 on a 100x200 image.
    (ann,) = parse_yolo_labels(["1 0.5 0.5 0.2 0.4"], 100, 200, CLASS_MAP)
    assert ann.species is Species.VESPA_VELUTINA
    assert ann.bbox.width == pytest.approx(20.0)
    assert ann.bbox.height == pytest.approx(80.0)
    assert ann.bbox.x == pytest.approx(40.0)  # (0.5 - 0.1) * 100
    assert ann.bbox.y == pytest.approx(60.0)  # (0.5 - 0.2) * 200


def test_class_map_and_unknown_id():
    anns = parse_yolo_labels(["0 0.5 0.5 0.1 0.1", "7 0.5 0.5 0.1 0.1"], 100, 100, CLASS_MAP)
    assert anns[0].species is Species.VESPA_CRABRO
    assert anns[1].species is Species.UNKNOWN  # id 7 not in the map


def test_blank_lines_ignored():
    assert parse_yolo_labels(["", "  ", "\n"], 100, 100, CLASS_MAP) == []


@pytest.mark.parametrize("bad", ["1 0.5 0.5 0.2", "1 0.5 0.5 0.2 0.4 0.9", "garbage"])
def test_malformed_line_raises(bad):
    with pytest.raises(ValueError, match="5 fields"):
        parse_yolo_labels([bad], 100, 100, CLASS_MAP)


def test_out_of_range_value_raises():
    with pytest.raises(ValueError, match="normalised"):
        parse_yolo_labels(["1 1.2 0.5 0.2 0.4"], 100, 100, CLASS_MAP)


def test_non_positive_image_size_raises():
    with pytest.raises(ValueError, match="image size"):
        parse_yolo_labels(["1 0.5 0.5 0.2 0.4"], 0, 100, CLASS_MAP)
