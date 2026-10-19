"""`AudioRecorder` over `sounddevice` (ALSA I²S) writing FLAC with `soundfile`.

Two ICS-43434 on one I²S bus give one stereo stream: left = entrance, right = colony
(ADR-0017), so both channels share one clock. The PortAudio callback only copies blocks into a
queue; a writer thread does the disk I/O, so the realtime thread never blocks. Libraries are
imported lazily (extra `capture`).
"""

import logging
import queue
import threading
import time
from typing import Any

_log = logging.getLogger("aristech.capture")
_CHANNELS = ("entrance", "colony")
_STALL_SECONDS = 2.0
_FLAT_PEAK = 1e-4  # a dead MEMS mic reads (near) constant zero


class SoundDeviceRecorder:
    """Continuous 2-channel input stream; segments are files opened and closed on demand."""

    def __init__(self, device: str | int | None = None, sample_rate: int = 48_000) -> None:
        """`device` is the ALSA device name or index; None is the default input."""
        self._device = device
        self._sample_rate = sample_rate
        self._stream: Any | None = None
        self._file: Any | None = None
        self._lock = threading.Lock()
        self._last_block = 0.0
        self._peaks = [0.0, 0.0]
        self._blocks: queue.Queue[Any] = queue.Queue()
        self._writer: threading.Thread | None = None
        self.overflows = 0
        self._write_error: Exception | None = None
        self._frames_written = 0

    def _callback(self, indata: Any, frames: int, time_info: Any, status: Any) -> None:
        self._last_block = time.monotonic()
        if status:
            self.overflows += 1
        self._peaks = [float(abs(indata[:, i]).max()) for i in range(len(_CHANNELS))]
        self._blocks.put(indata.copy())

    def _write(self, block: Any) -> None:
        with self._lock:
            if self._file is None or self._write_error is not None:
                return
            try:
                self._file.write(block)
                self._frames_written += len(block)
            except Exception as error:  # noqa: BLE001 — surfaced by healthy(), never swallowed
                self._write_error = error

    def _write_blocks(self) -> None:
        while True:
            block = self._blocks.get()
            if block is None:
                return
            self._write(block)

    def drain(self) -> None:
        """Write every queued block now (used on stop and by tests)."""
        while True:
            try:
                block = self._blocks.get_nowait()
            except queue.Empty:
                return
            if block is not None:
                self._write(block)

    def healthy(self) -> bool:
        """Open the stream on first call; healthy while blocks keep arriving.

        A stalled stream is closed so that the next call reopens it. A failed write (e.g. SSD
        I/O error) drops the open file and answers False, so the use case closes the segment and
        opens a new one on the next tick.
        """
        if self._write_error is not None:
            _log.warning("audio write failed: %s", self._write_error)
            with self._lock:
                broken, self._file = self._file, None
                self._write_error = None
            if broken is not None:
                try:
                    broken.close()
                except Exception:  # noqa: BLE001 — the file is already broken
                    _log.debug("closing the broken audio file failed", exc_info=True)
            return False
        if self._stream is not None and time.monotonic() - self._last_block >= _STALL_SECONDS:
            _log.warning("audio stream stalled; reopening (overflows so far: %d)", self.overflows)
            self._close_stream()
            return False
        if self._stream is None:
            try:
                import sounddevice

                self._stream = sounddevice.InputStream(
                    device=self._device,
                    channels=len(_CHANNELS),
                    samplerate=self._sample_rate,
                    dtype="float32",
                    callback=self._callback,
                )
                self._stream.start()
                self._last_block = time.monotonic()
                if self._writer is None:
                    self._writer = threading.Thread(target=self._write_blocks, daemon=True)
                    self._writer.start()
            except Exception:  # noqa: BLE001 — any device error means "not healthy", retried
                _log.debug("audio stream unavailable", exc_info=True)
                self._stream = None
                return False
        return time.monotonic() - self._last_block < _STALL_SECONDS

    def missing_channels(self) -> tuple[str, ...]:
        """Channels whose last block peak is flat."""
        return tuple(n for n, p in zip(_CHANNELS, self._peaks, strict=True) if p < _FLAT_PEAK)

    def start_segment(self, path: str) -> None:
        """Open a 24-bit FLAC file at `path`; samples flow into it from the next block."""
        import soundfile

        self.drain()
        new_file = soundfile.SoundFile(
            path, "w", self._sample_rate, len(_CHANNELS), "PCM_24", format="FLAC"
        )
        with self._lock:
            old, self._file = self._file, new_file
            self._frames_written = 0
        if old is not None:
            old.close()

    def stop_segment(self) -> float:
        """Flush queued blocks, close the FLAC file, return the seconds written to it."""
        self.drain()
        with self._lock:
            old, self._file = self._file, None
            written = self._frames_written / self._sample_rate
            self._frames_written = 0
        if old is not None:
            old.close()
        return written

    def settings(self) -> dict[str, str | int | float]:
        """Sample rate, bit depth and channel order."""
        return {
            "sample_rate_hz": self._sample_rate,
            "bit_depth": 24,
            "channels": ",".join(_CHANNELS),
        }

    def close(self) -> None:
        """Close the segment, the stream and the writer thread."""
        self.stop_segment()
        self._close_stream()
        if self._writer is not None:
            self._blocks.put(None)
            self._writer.join(timeout=2)
            self._writer = None

    def _close_stream(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
