from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from aristech.domain import VideoFrame


def test_video_frame_stores_fields_and_opaque_pixels():
    now = datetime(2026, 5, 20)
    pixels = [[0, 1], [2, 3]]  # opaque container; domain does not know numpy
    frame = VideoFrame(pixels=pixels, width=2, height=2, timestamp=now)
    assert frame.pixels is pixels
    assert frame.width == 2
    assert frame.height == 2
    assert frame.timestamp == now


def test_video_frame_is_frozen():
    frame = VideoFrame(pixels=None, width=1, height=1, timestamp=datetime(2026, 5, 20))
    with pytest.raises(FrozenInstanceError):
        frame.width = 99  # type: ignore[misc]
