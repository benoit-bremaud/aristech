from dataclasses import FrozenInstanceError

import pytest

from aristech.domain import BoundingBox, Point2D


def test_bounding_box_area():
    bbox = BoundingBox(x=1.0, y=2.0, width=4.0, height=3.0)
    assert bbox.area == 12.0


def test_bounding_box_center():
    bbox = BoundingBox(x=0.0, y=0.0, width=10.0, height=6.0)
    center = bbox.center
    assert isinstance(center, Point2D)
    assert center.x == 5.0
    assert center.y == 3.0


def test_bounding_box_zero_dimensions_allowed():
    bbox = BoundingBox(x=0.0, y=0.0, width=0.0, height=0.0)
    assert bbox.area == 0.0


@pytest.mark.parametrize(
    ("width", "height"),
    [(-1.0, 1.0), (1.0, -1.0), (-1.0, -1.0)],
)
def test_bounding_box_rejects_negative_dimensions(width: float, height: float):
    with pytest.raises(ValueError):
        BoundingBox(x=0.0, y=0.0, width=width, height=height)


def test_bounding_box_is_frozen():
    bbox = BoundingBox(x=0.0, y=0.0, width=1.0, height=1.0)
    with pytest.raises(FrozenInstanceError):
        bbox.x = 5.0  # type: ignore[misc]


def test_point2d_equality_and_frozen():
    assert Point2D(1.0, 2.0) == Point2D(1.0, 2.0)
    assert Point2D(1.0, 2.0) != Point2D(2.0, 1.0)
    with pytest.raises(FrozenInstanceError):
        Point2D(1.0, 2.0).x = 3.0  # type: ignore[misc]
