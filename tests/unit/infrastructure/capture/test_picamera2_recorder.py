import sys
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
        return self.frames.pop(0)

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


def test_starts_1080p30_into_a_ten_second_ring(camera: _FakeCamera) -> None:
    recorder = Picamera2Recorder()

    assert recorder.healthy() is True
    assert camera.recording
    assert camera.config["main"] == {"size": (1920, 1080)}
    assert camera.output.buffer_duration_ms == 10_000


def test_motion_is_a_luma_change_above_threshold(camera: _FakeCamera) -> None:
    recorder = Picamera2Recorder()
    recorder.healthy()
    camera.frames = [_frame(100), _frame(102), _frame(150)]

    assert [recorder.motion_detected() for _ in range(3)] == [False, False, True]


def test_clip_opens_and_closes_an_output_on_the_ring(camera: _FakeCamera) -> None:
    recorder = Picamera2Recorder()
    recorder.healthy()

    recorder.start_clip("c.mp4")
    recorder.start_clip("ignored.mp4")
    recorder.stop_clip()

    assert camera.output.outputs == ["c.mp4"]
    assert camera.output.open is False


def test_settings_carry_exposure(camera: _FakeCamera) -> None:
    recorder = Picamera2Recorder()
    recorder.healthy()

    assert recorder.settings()["ExposureTime"] == 1000


def test_no_camera_is_unhealthy_and_inert(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "picamera2", None)
    recorder = Picamera2Recorder()

    assert recorder.healthy() is False
    assert recorder.motion_detected() is False
    recorder.start_clip("x.mp4")
    recorder.close()
    assert recorder.settings() == {"resolution": "1920x1080", "fps": 30}


def test_close_releases_the_camera(camera: _FakeCamera) -> None:
    recorder = Picamera2Recorder()
    recorder.healthy()

    recorder.close()

    assert camera.closed and not camera.recording


def test_camera_lost_mid_run_is_released(camera: _FakeCamera) -> None:
    recorder = Picamera2Recorder()
    recorder.healthy()
    camera.frames = []

    assert recorder.motion_detected() is False
    assert camera.closed
    assert recorder.healthy() is False
    assert recorder.healthy() is True


def test_settings_survive_a_metadata_error(camera: _FakeCamera) -> None:
    recorder = Picamera2Recorder()
    recorder.healthy()

    def broken() -> dict[str, Any]:
        raise RuntimeError("camera gone")

    camera.capture_metadata = broken  # type: ignore[method-assign]

    assert recorder.settings() == {"resolution": "1920x1080", "fps": 30}
