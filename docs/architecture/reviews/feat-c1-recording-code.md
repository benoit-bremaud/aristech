# Pre-push review — `feat/c1-recording-code`

> **Scope**: C1 recording code after the signed gate `capture-rig`: domain (`RigState`,
> `SegmentMetadata`, `daylight_window`), ports `Clock` / `CameraRecorder` / `AudioRecorder` /
> `SegmentStore`, use case `RecordCampaign`, adapters in `infrastructure/capture/` (Picamera2,
> sounddevice + soundfile, file store, system clock) behind the new `capture` extra, CLI
> `aristech-record`, tests with hand-written fakes, spec / traceability / INSTALL updates.

## Checks

- `ruff check`, `ruff format --check`, strict `mypy`: clean.
- Unit tests: 160 passed, 2 skipped (OpenCV absent locally); coverage 95 % overall, new modules
  97–100 % except `system_clock.py` 77 % (the real `timedatectl` probe, not run in tests).
- Dependency rule: a unit test checks that `domain` and `application` import none of picamera2,
  sounddevice, soundfile; adapters import them lazily.
- Daylight window checked against Paris equinox sunrise/sunset (± 3 min) and polar day/night.
- Secrets scan: see the push gate (gitleaks in CI).

## 🔴 Must Have (all fixed)

- A stalled audio stream stayed dead for the whole campaign → closed on stall and reopened.
- Any adapter error in a tick (disk, encoder, corrupt sidecar) ended the recorder → a failed
  step now enters FAULT, releases segments and is retried next tick; unreadable sidecars are
  skipped by rotation.

## 🟡 Should Have

- Fixed: disk writes in the PortAudio callback → callback queues blocks, a writer thread writes;
  overflows counted and logged on stall.
- Fixed: camera lost mid-clip left a stale clip → `healthy()` answers False once after a loss so
  the clip is closed.
- Fixed: `missing_inputs` was a close-time snapshot → accumulated over the segment's life.
- Fixed: orphan segments (no sidecar after a power cut) were never rotated → dated by file time.
- Fixed: full disk rescanned every tick → "nothing to rotate" cached until the next sidecar.
- Deferred: a camera that freezes without raising is not detected (documented limit); revisit
  with frame-age checks once real hardware shows how Picamera2 fails.

## 🔵 Nice to Have (fixed)

- RECORDING log line no longer prints an empty "missing inputs"; camera metadata read is
  best-effort; UTC-date limit of the daylight window documented.

## Not verifiable here

- Field ACs AC1 (clap sync), AC2 (7 days), AC6 (ruler), AC9 (power) need the hardware.
