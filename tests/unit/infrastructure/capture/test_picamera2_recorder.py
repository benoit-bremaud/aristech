import sys
import threading
import time
import types
from typing import Any

import numpy
import pytest

from aristech.infrastructure.capture import Picamera2Recorder


class _FakeCircular:
    def __init__(self, buffer_duration_ms: int) -> None:
        self.buffer_duration_ms = buffer_duration_ms
        self.outputs: list[str] = []
        self.open = False

    def open_output(self, output: Any) -> None:
        self.outputs.append(output.path)
        self.open = True

    def close_output(self) -> None:
        self.open = False


class _FakeCamera:
    def __init__(self) -> None:
        self.frames: list[Any] = []
        self.consumed = threading.Event()
        self.recording = False
        self.closed = False

    def create_video_configuration(self, **kwargs: Any) -> dict[str, Any]:
        return kwargs

    def configure(self, config: dict[str, Any]) -> None:
        self.config = config

    def start_recording(self, encoder: Any, output: Any) -> None:
        self.output = output
        self.recording = True

    def stop_recording(self) -> None:
        self.recording = False

    def close(self) -> None:
        self.closed = True

    def capture_array(self, stream: str) -> Any:
        if not self.frames:
            raise RuntimeError("camera gone")
        frame = self.frames.pop(0)
        self.consumed.set() if not self.frames else None
        return frame

    def capture_metadata(self) -> dict[str, Any]:
        return {"ExposureTime": 1000, "AnalogueGain": 1.5}


@pytest.fixture
def camera(monkeypatch: pytest.MonkeyPatch) -> _FakeCamera:
    fake = _FakeCamera()
    package = types.ModuleType("picamera2")
    package.Picamera2 = lambda: fake  # type: ignore[attr-defined]
    encoders = types.SimpleNamespace(H264Encoder=lambda: "h264")
    outputs = types.SimpleNamespace(
        CircularOutput2=_FakeCircular, PyavOutput=lambda path: types.SimpleNamespace(path=path)
    )
    monkeypatch.setitem(sys.modules, "picamera2", package)
    monkeypatch.setitem(sys.modules, "picamera2.encoders", encoders)
    monkeypatch.setitem(sys.modules, "picamera2.outputs", outputs)
    return fake


def _frame(level: int) -> Any:
    return numpy.full((360, 320), level, dtype=numpy.uint8)


def _recorder(**kwargs: Any) -> Picamera2Recorder:
    return Picamera2Recorder(pre_roll_seconds=0.05, motion_hz=1000, **kwargs)


def _wait_lost(recorder: Picamera2Recorder) -> None:
    deadline = time.monotonic() + 2
    while not recorder._lost and time.monotonic() < deadline:
        time.sleep(0.01)


def test_starts_1080p30_with_a_pre_roll_ring(camera: _FakeCamera) -> None:
    recorder = Picamera2Recorder()
    camera.frames = [_frame(100)] * 1000

    assert recorder.healthy() is True
    assert camera.recording
    assert camera.config["main"] == {"size": (1920, 1080)}
    assert camera.config["controls"] == {"FrameRate": 30}
    assert camera.output.buffer_duration_ms == 5_000
    recorder.close()


def test_motion_between_ticks_is_latched_until_read(camera: _FakeCamera) -> None:
    camera.frames = [_frame(100), _frame(150), _frame(150)]
    recorder = _recorder()
    recorder.healthy()
    camera.consumed.wait(2)

    assert recorder.motion_detected() is True
    assert recorder.motion_detected() is False
    recorder.close()


def test_still_scene_is_no_motion(camera: _FakeCamera) -> None:
    camera.frames = [_frame(100), _frame(102), _frame(101)]
    recorder = _recorder()
    recorder.healthy()
    camera.consumed.wait(2)

    assert recorder.motion_detected() is False
    recorder.close()


def test_clip_closes_only_after_the_ring_has_flushed(camera: _FakeCamera) -> None:
    camera.frames = [_frame(100)] * 10_000
    recorder = Picamera2Recorder(pre_roll_seconds=0.2, motion_hz=10)
    recorder.healthy()

    recorder.start_clip("c.mp4")
    recorder.start_clip("ignored.mp4")
    recorder.stop_clip()

    assert camera.output.open is True
    time.sleep(0.4)
    assert camera.output.open is False
    assert camera.output.outputs == ["c.mp4"]
    recorder.close()


def test_new_clip_during_flush_closes_the_old_one_at_once(camera: _FakeCamera) -> None:
    camera.frames = [_frame(100)] * 10_000
    recorder = Picamera2Recorder(pre_roll_seconds=5, motion_hz=10)
    recorder.healthy()
    recorder.start_clip("a.mp4")
    recorder.stop_clip()

    recorder.start_clip("b.mp4")

    assert camera.output.outputs == ["a.mp4", "b.mp4"]
    assert camera.output.open is True
    recorder.close()
    assert camera.output.open is False


def test_settings_carry_exposure(camera: _FakeCamera) -> None:
    camera.frames = [_frame(100)] * 1000
    recorder = Picamera2Recorder()
    recorder.healthy()

    assert recorder.settings()["ExposureTime"] == 1000
    recorder.close()


def test_settings_survive_a_metadata_error(camera: _FakeCamera) -> None:
    camera.frames = [_frame(100)] * 1000
    recorder = Picamera2Recorder()
    recorder.healthy()

    def broken() -> dict[str, Any]:
        raise RuntimeError("camera gone")

    camera.capture_metadata = broken  # type: ignore[method-assign]

    assert recorder.settings() == {"resolution": "1920x1080", "fps": 30}
    recorder.close()


def test_no_camera_is_unhealthy_and_inert(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "picamera2", None)
    recorder = Picamera2Recorder()

    assert recorder.healthy() is False
    assert recorder.motion_detected() is False
    recorder.start_clip("x.mp4")
    recorder.stop_clip()
    recorder.close()
    assert recorder.settings() == {"resolution": "1920x1080", "fps": 30}


def test_camera_lost_mid_run_is_reported_once_then_retried(camera: _FakeCamera) -> None:
    recorder = _recorder()
    recorder.healthy()
    _wait_lost(recorder)

    assert recorder.healthy() is False
    assert camera.closed
    camera.frames = [_frame(100)] * 1000
    assert recorder.healthy() is True
    recorder.close()
