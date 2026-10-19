"""Capture-rig adapters (ADR-0017). Hardware libraries load lazily: extra `capture`."""

from aristech.infrastructure.capture.file_segment_store import FileSegmentStore
from aristech.infrastructure.capture.picamera2_recorder import Picamera2Recorder
from aristech.infrastructure.capture.sounddevice_recorder import SoundDeviceRecorder
from aristech.infrastructure.capture.system_clock import SystemClock

__all__ = ["FileSegmentStore", "Picamera2Recorder", "SoundDeviceRecorder", "SystemClock"]
