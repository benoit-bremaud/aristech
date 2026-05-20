from dataclasses import FrozenInstanceError
from datetime import datetime
from uuid import UUID, uuid4

import pytest

from aristech.domain import Point3D, Target


def _position() -> Point3D:
    return Point3D(1.0, 2.0, 3.0)


def test_target_stores_fields():
    now = datetime(2026, 5, 20)
    tid = uuid4()
    target = Target(id=tid, position=_position(), confidence=0.8, last_seen=now)
    assert target.id == tid
    assert target.position == _position()
    assert target.confidence == 0.8
    assert target.last_seen == now


@pytest.mark.parametrize("confidence", [0.0, 0.5, 1.0])
def test_target_accepts_confidence_within_bounds(confidence: float):
    target = Target.new(_position(), confidence, datetime(2026, 5, 20))
    assert target.confidence == confidence


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_target_rejects_confidence_out_of_bounds(confidence: float):
    with pytest.raises(ValueError):
        Target.new(_position(), confidence, datetime(2026, 5, 20))


def test_target_new_generates_unique_uuids():
    now = datetime(2026, 5, 20)
    first = Target.new(_position(), 0.5, now)
    second = Target.new(_position(), 0.5, now)
    assert isinstance(first.id, UUID)
    assert first.id != second.id


def test_target_is_frozen():
    target = Target.new(_position(), 0.5, datetime(2026, 5, 20))
    with pytest.raises(FrozenInstanceError):
        target.confidence = 0.9  # type: ignore[misc]
