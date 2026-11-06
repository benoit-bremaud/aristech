"""Capture-rig ports (ADR-0017): each has a real adapter and a hand-written test fake."""

from collections.abc import Mapping
from datetime import datetime
from typing import Protocol

from aristech.domain import SegmentMetadata

Settings = Mapping[str, str | int | float]


class Clock(Protocol):
    """UTC wall time for segments whose device has no better time (spec AC1).

    Segment times come from the device where it knows better (audio sample times, a clip's
    first-frame sensor time), otherwise from this clock; all are UTC wall time.
    """

    def now(self) -> datetime:
        """Current time, timezone-aware UTC."""
        ...

    def source(self) -> str:
        """`ntp`, `rtc` or `unsynced` (spec A4)."""
        ...


class CameraRecorder(Protocol):
    """Camera with a RAM ring buffer; a clip starts with the buffered pre-roll."""

    def healthy(self) -> bool:
        """True while frames arrive; opens the camera on first call.

        False after a loss: the camera has been released, which writes the ring into an open clip.
        """
        ...

    def motion_detected(self) -> bool:
        """True if the region of interest changed since the last call."""
        ...

    def start_clip(self, path: str) -> datetime | None:
        """Write the buffered pre-roll to `path`, then keep writing live frames.

        Return the UTC time of the clip's first frame (its sensor timestamp), or None if it
        is not known; the use case then dates the clip one ring before the tick (spec AC1).
        """
        ...

    def stop_clip(self) -> None:
        """Close the open clip; no-op if none."""
        ...

    def settings(self) -> Settings:
        """Resolution, fps, exposure and gain, for the sidecar."""
        ...

    def close(self) -> None:
        """Write the buffered frames to the last clip, then release the camera.

        A clip stopped less than one ring before, while the camera was healthy, therefore ends at
        the release; safe to call more than once.
        """
        ...


class AudioRecorder(Protocol):
    """Two-channel I²S stream (entrance + colony) written as segments."""

    def healthy(self) -> bool:
        """True while samples arrive; opens the stream on first call."""
        ...

    def missing_channels(self) -> tuple[str, ...]:
        """Channels currently silent or flat (spec A2), e.g. `("colony",)`."""
        ...

    def start_segment(self, path: str) -> None:
        """Start writing samples to `path`."""
        ...

    def stop_segment(self) -> tuple[datetime, datetime] | None:
        """Close the open segment; return the UTC times of its first and last sample.

        None if nothing was written. The use case dates the sidecar from this span, so it
        matches the samples even when the stream starts late or the tick is slow (spec AC1).
        """
        ...

    def settings(self) -> Settings:
        """Sample rate, bit depth, channel names, for the sidecar."""
        ...

    def close(self) -> None:
        """Release the stream; safe to call more than once."""
        ...


class SegmentStore(Protocol):
    """Where segments and their sidecars live, with oldest-first rotation (spec A1)."""

    def path_for(self, kind: str, start: datetime) -> str:
        """A new file path for a segment of `kind` (`audio` / `video`) starting at `start`."""
        ...

    def write_sidecar(self, path: str, metadata: SegmentMetadata) -> None:
        """Store the metadata next to the segment at `path`."""
        ...

    def free_fraction(self) -> float:
        """Free space on the storage, 0.0 to 1.0."""
        ...

    def delete_oldest_unflagged(self) -> bool:
        """Delete the oldest non-flagged segment; False if there is none."""
        ...
