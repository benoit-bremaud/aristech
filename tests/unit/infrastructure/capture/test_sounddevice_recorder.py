import sys
import types
from typing import Any

import numpy
import pytest

from aristech.infrastructure.capture import SoundDeviceRecorder


class _FakeStream:
    def __init__(self, callback: Any, **kwargs: Any) -> None:
        self.callback = callback
        self.kwargs = kwargs
        self.started = self.closed = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.started = False

    def close(self) -> None:
        self.closed = True


class _FakeSoundFile:
    def __init__(self, path: str, *args: Any, **kwargs: Any) -> None:
        self.path = path
        self.args = args
        self.kwargs = kwargs
        self.blocks: list[Any] = []
        self.closed = False

    def write(self, block: Any) -> None:
        self.blocks.append(block)

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def streams(monkeypatch: pytest.MonkeyPatch) -> list[_FakeStream]:
    created: list[_FakeStream] = []

    def input_stream(**kwargs: Any) -> _FakeStream:
        stream = _FakeStream(**kwargs)
        created.append(stream)
        return stream

    monkeypatch.setitem(sys.modules, "sounddevice", types.SimpleNamespace(InputStream=input_stream))
    monkeypatch.setitem(sys.modules, "soundfile", types.SimpleNamespace(SoundFile=_FakeSoundFile))
    return created


def test_opens_a_two_channel_48k_stream(streams: list[_FakeStream]) -> None:
    recorder = SoundDeviceRecorder()

    assert recorder.healthy() is True
    assert streams[0].kwargs["channels"] == 2
    assert streams[0].kwargs["samplerate"] == 48_000


def test_segment_receives_blocks_as_24_bit_flac(streams: list[_FakeStream]) -> None:
    recorder = SoundDeviceRecorder()
    recorder.healthy()
    recorder.start_segment("a.flac")
    block = numpy.full((4, 2), 0.1, dtype="float32")

    streams[0].callback(block, 4, None, None)
    file = recorder._file
    written = recorder.stop_segment()

    assert written == 4 / 48_000
    assert isinstance(file, _FakeSoundFile)
    assert file.blocks and file.closed
    assert file.args[3] == "PCM_24" and file.kwargs["format"] == "FLAC"


def test_flat_channel_is_reported_missing(streams: list[_FakeStream]) -> None:
    recorder = SoundDeviceRecorder()
    recorder.healthy()
    block = numpy.zeros((4, 2), dtype="float32")
    block[:, 0] = 0.2

    streams[0].callback(block, 4, None, None)

    assert recorder.missing_channels() == ("colony",)


def test_device_error_is_unhealthy(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken(**kwargs: Any) -> None:
        raise OSError("no I2S device")

    monkeypatch.setitem(sys.modules, "sounddevice", types.SimpleNamespace(InputStream=broken))

    assert SoundDeviceRecorder().healthy() is False


def test_close_stops_the_stream(streams: list[_FakeStream]) -> None:
    recorder = SoundDeviceRecorder()
    recorder.healthy()

    recorder.close()
    recorder.close()

    assert streams[0].closed
    assert recorder.settings()["channels"] == "entrance,colony"


def test_stalled_stream_is_closed_then_reopened(
    streams: list[_FakeStream], monkeypatch: pytest.MonkeyPatch
) -> None:
    recorder = SoundDeviceRecorder()
    recorder.healthy()
    recorder._last_block -= 10

    assert recorder.healthy() is False
    assert streams[0].closed
    assert recorder.healthy() is True
    assert len(streams) == 2
    recorder.close()


def test_overflow_status_is_counted(streams: list[_FakeStream]) -> None:
    recorder = SoundDeviceRecorder()
    recorder.healthy()

    streams[0].callback(numpy.zeros((4, 2), dtype="float32"), 4, None, "input overflow")

    assert recorder.overflows == 1
    recorder.close()


def test_write_failure_drops_the_file_and_reports_unhealthy(streams: list[_FakeStream]) -> None:
    recorder = SoundDeviceRecorder()
    recorder.healthy()
    recorder.start_segment("a.flac")
    file = recorder._file
    assert isinstance(file, _FakeSoundFile)

    def broken(block: Any) -> None:
        raise OSError("SSD I/O error")

    file.write = broken  # type: ignore[method-assign]
    streams[0].callback(numpy.zeros((4, 2), dtype="float32"), 4, None, None)
    recorder.drain()

    assert recorder.healthy() is False
    assert file.closed and recorder._file is None
    assert recorder.healthy() is True
    recorder.close()
