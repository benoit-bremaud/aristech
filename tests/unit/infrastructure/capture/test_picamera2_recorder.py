import sys
import threading
import time
import types
from datetime import UTC, datetime, timedelta
from typing import Any

import numpy
import pytest

from aristech.infrastructure.capture import Picamera2Recorder, picamera2_recorder


class _FakeCircular:
    def __init__(self, buffer_duration_ms: int) -> None:
        self.buffer_duration_ms = buffer_duration_ms
        self.outputs: list[str] = []
        self.open = False
        self._time_offset = 3_000_000  # the first keyframe written, from the encoder origin
        self.keyframe_delay = 0.0  # the ring drops frames until a keyframe is one ring old
        self.output: Any = None
        self.recording = True  # started by start_recording

    def open_output(self, output: Any) -> None:
        output.start()
        output._add_stream("video", "h264")
        self.outputs.append(output.path)
        self.output, self.open = output, True
        output.outputframe(b"audio", True, 0, None, True)
        # The ring rebases its first keyframe to zero.
        self.timer = threading.Timer(self.keyframe_delay, output.outputframe, (b"key", True, 0))
        self.timer.start()

    def close_output(self) -> None:
        if not self.open:
            raise RuntimeError("No underlying output has been opened")
        self.timer.cancel()
        self.open = False  # detached before stopping, as upstream
        self.output.stop()

    def stop(self) -> None:
        # CircularOutput2.stop() flushes the whole ring into the attached output, then stops it.
        if not self.recording:
            raise RuntimeError("Circular output was not started")
        self.recording = False
        if self.open:
            self.timer.cancel()
            self.output.outputframe(b"ring", True, 0, None, False)
            self.output.stop()
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
        self.encoder = encoder
        self.output = output
        self.recording = True

    def stop_encoder(self) -> None:
        self.output.stop()

    def stop(self) -> None:
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


class _FakePyav:
    def __init__(self, path: str) -> None:
        self.path = path
        self.frames: list[bytes] = []
        self.calls: list[str] = []

    def start(self) -> None:
        self.calls.append("start")

    def _add_stream(self, stream: str, codec: str) -> None:
        self.calls.append("add_stream")

    def stop(self) -> None:
        self.calls.append("stop")

    def outputframe(
        self, frame: bytes, keyframe: bool, timestamp: int, packet: Any, audio: bool
    ) -> None:
        self.frames.append(frame)


@pytest.fixture
def camera(monkeypatch: pytest.MonkeyPatch) -> _FakeCamera:
    fake = _FakeCamera()
    package = types.ModuleType("picamera2")
    package.Picamera2 = lambda: fake  # type: ignore[attr-defined]
    encoders = types.SimpleNamespace(
        H264Encoder=lambda iperiod: types.SimpleNamespace(iperiod=iperiod, firsttimestamp=1_000_000)
    )
    outputs = types.SimpleNamespace(CircularOutput2=_FakeCircular, PyavOutput=_FakePyav)
    monkeypatch.setitem(sys.modules, "picamera2", package)
    monkeypatch.setitem(sys.modules, "picamera2.encoders", encoders)
    monkeypatch.setitem(sys.modules, "picamera2.outputs", outputs)
    return fake


def _frame(level: int) -> Any:
    return numpy.full((360, 320), level, dtype=numpy.uint8)


def _recorder(**kwargs: Any) -> Picamera2Recorder:
    return Picamera2Recorder(ring_seconds=0.05, motion_hz=1000, **kwargs)


def _wait_lost(recorder: Picamera2Recorder) -> None:
    deadline = time.monotonic() + 2
    while not recorder._lost and time.monotonic() < deadline:
        time.sleep(0.01)


def test_starts_1080p30_with_a_ring_and_a_one_second_gop(camera: _FakeCamera) -> None:
    recorder = Picamera2Recorder()
    camera.frames = [_frame(100)] * 1000

    assert recorder.healthy() is True
    assert camera.recording
    assert camera.config["main"] == {"size": (1920, 1080)}
    assert camera.config["controls"] == {"FrameRate": 30}
    assert camera.output.buffer_duration_ms == 8_000
    assert camera.encoder.iperiod == 30
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
    recorder = Picamera2Recorder(ring_seconds=0.2, motion_hz=10)
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
    recorder = Picamera2Recorder(ring_seconds=5, motion_hz=10)
    recorder.healthy()
    recorder.start_clip("a.mp4")
    recorder.stop_clip()

    recorder.start_clip("b.mp4")

    assert camera.output.outputs == ["a.mp4", "b.mp4"]
    assert camera.output.open is True
    recorder.close()
    assert camera.output.open is False


def test_close_flushes_the_ring_into_the_open_clip(camera: _FakeCamera) -> None:
    camera.frames = [_frame(100)] * 10_000
    recorder = Picamera2Recorder(ring_seconds=5, motion_hz=10)
    recorder.healthy()
    recorder.start_clip("a.mp4")
    clip = camera.output.output

    recorder.close()

    assert clip.frames[-1] == b"ring"
    assert clip.calls.count("stop") == 1


def test_close_flushes_the_ring_into_a_clip_pending_close(camera: _FakeCamera) -> None:
    # #180: the shutdown drops the pending close instead of cutting the last ring.
    camera.frames = [_frame(100)] * 10_000
    recorder = Picamera2Recorder(ring_seconds=5, motion_hz=10)
    recorder.healthy()
    recorder.start_clip("a.mp4")
    recorder.stop_clip()
    clip = camera.output.output

    recorder.close()

    assert clip.frames[-1] == b"ring"
    assert clip.calls.count("stop") == 1


def test_close_after_the_pending_close_fired_stops_nothing_twice(camera: _FakeCamera) -> None:
    camera.frames = [_frame(100)] * 10_000
    recorder = Picamera2Recorder(ring_seconds=0.05, motion_hz=10)
    recorder.healthy()
    recorder.start_clip("a.mp4")
    recorder.stop_clip()
    clip = camera.output.output
    time.sleep(0.2)

    recorder.close()

    assert b"ring" not in clip.frames
    assert clip.calls.count("stop") == 1


def test_close_waits_for_a_pending_close_already_finishing_the_file(
    camera: _FakeCamera,
) -> None:
    camera.frames = [_frame(100)] * 10_000
    recorder = Picamera2Recorder(ring_seconds=0.01, motion_hz=10)
    recorder.healthy()
    recorder.start_clip("a.mp4")
    clip = camera.output.output._output
    entered, release = threading.Event(), threading.Event()

    def slow_stop() -> None:
        entered.set()
        release.wait(2)
        clip.calls.append("stop")

    clip.stop = slow_stop
    recorder.stop_clip()
    assert entered.wait(2)
    closer = threading.Thread(target=recorder.close)
    closer.start()

    closer.join(0.1)
    assert closer.is_alive()  # still waiting for the file to be finished
    release.set()
    closer.join(2)
    assert not closer.is_alive()
    assert clip.calls.count("stop") == 1


def test_release_goes_on_when_stopping_the_camera_fails(camera: _FakeCamera) -> None:
    camera.frames = [_frame(100)] * 10_000
    recorder = Picamera2Recorder(ring_seconds=5, motion_hz=10)
    recorder.healthy()
    recorder.start_clip("a.mp4")
    clip = camera.output.output

    def dead() -> None:
        raise RuntimeError("camera gone")

    camera.stop = dead  # type: ignore[method-assign]
    recorder.close()

    assert clip.frames[-1] == b"ring"  # the encoder stopped first and finished the file
    assert camera.closed


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


def test_start_clip_returns_the_first_frame_sensor_time_in_utc(
    camera: _FakeCamera, monkeypatch: pytest.MonkeyPatch
) -> None:
    epoch = datetime(2026, 6, 1, 12, tzinfo=UTC)
    monkeypatch.setattr(
        picamera2_recorder, "_boot_to_utc", lambda us: epoch + timedelta(microseconds=us)
    )
    camera.frames = [_frame(100)] * 10_000
    recorder = _recorder()
    recorder.healthy()

    first_frame = recorder.start_clip("c.mp4")

    # encoder origin 1 s + ring offset 3 s: the keyframe the clip starts on
    assert first_frame == epoch + timedelta(seconds=4)
    recorder.close()
    pyav = camera.output.output._output
    assert pyav.frames == [b"audio", b"key", b"ring"]
    assert pyav.calls == ["start", "add_stream", "stop"]


def test_start_clip_waits_up_to_one_gop_for_the_first_keyframe(camera: _FakeCamera) -> None:
    camera.frames = [_frame(100)] * 10_000
    recorder = _recorder()
    recorder.healthy()
    camera.output.keyframe_delay = 0.9

    assert recorder.start_clip("c.mp4") is not None
    recorder.close()


def test_first_frame_time_is_unknown_if_the_ring_offset_is_missing(camera: _FakeCamera) -> None:
    camera.frames = [_frame(100)] * 10_000
    recorder = _recorder()
    recorder.healthy()
    del camera.output._time_offset

    assert recorder.start_clip("c.mp4") is None
    assert camera.output.outputs == ["c.mp4"]
    recorder.close()


def test_first_frame_time_is_unknown_if_no_frame_arrives(
    camera: _FakeCamera, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(picamera2_recorder, "_FIRST_FRAME_TIMEOUT", 0.01)
    camera.frames = [_frame(100)] * 10_000
    recorder = _recorder()
    recorder.healthy()
    camera.output.keyframe_delay = 0.2

    assert recorder.start_clip("c.mp4") is None
    recorder.close()


def test_boot_time_maps_to_utc_by_its_age(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(picamera2_recorder.time, "clock_gettime_ns", lambda clock: 10_000_000_000)
    before = datetime.now(UTC)

    utc = picamera2_recorder._boot_to_utc(8_000_000)  # 2 s before the boot clock's now

    assert before - timedelta(seconds=2) <= utc <= datetime.now(UTC) - timedelta(seconds=2)
