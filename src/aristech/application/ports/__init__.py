"""Ports: `Protocol`s the use cases depend on and adapters implement."""

from aristech.application.ports.capture import AudioRecorder, CameraRecorder, Clock, SegmentStore
from aristech.application.ports.hornet_detector import HornetDetector
from aristech.application.ports.notifier import Notifier
from aristech.application.ports.video_source import VideoSource

__all__ = [
    "AudioRecorder",
    "CameraRecorder",
    "Clock",
    "HornetDetector",
    "Notifier",
    "SegmentStore",
    "VideoSource",
]
