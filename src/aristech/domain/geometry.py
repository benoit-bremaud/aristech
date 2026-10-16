"""Image-plane geometry, in pixels."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BoundingBox:
    """Axis-aligned box: top-left corner (`x`, `y`) and non-negative size."""

    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width < 0 or self.height < 0:
            raise ValueError("BoundingBox dimensions must be non-negative")

    @property
    def center(self) -> "Point2D":
        """Centre of the box."""
        return Point2D(self.x + self.width / 2, self.y + self.height / 2)

    @property
    def area(self) -> float:
        """Width times height."""
        return self.width * self.height


@dataclass(frozen=True, slots=True)
class Point2D:
    """A point in the image plane."""

    x: float
    y: float
