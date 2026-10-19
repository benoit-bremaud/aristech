# QA — C1 recorder on a laptop (2026-10-19)

> **Scope**: `aristech-record` at `bac603d` run for 20 s on a Linux laptop (no camera, default
> ALSA input as the "I²S" device). No Raspberry Pi hardware yet: camera, I²S mics, NVMe and the
> field ACs are out of reach.

## Command

```bash
timeout -s INT 20 .venv/bin/aristech-record --rig-id qa-laptop --hive-id none --site home \
  --latitude 48.85 --longitude 2.35 --output <scratch>/qa1 --software-version bac603d
```

## Observed

| Check | Result |
|---|---|
| Daylight window at 09:18 UTC, Paris | in window, recording started ✅ |
| No camera → DEGRADED, audio goes on (spec A3) | `rig idle -> degraded (missing inputs: camera, entrance, colony)` ✅ |
| Ctrl-C closes the open segment (spec A5) | `stopped by the operator`, FLAC + sidecar written ✅ |
| FLAC format | 48 kHz, 2 channels, PCM_24 ✅ |
| Sidecar fields (AC3) | rig, hive, site, kind, trigger, start/end UTC, `clock_source: ntp`, version, settings, missing inputs ✅ |
| Flat channels reported (spec A2) | laptop input returned silence (peak 0) → both channels listed missing ✅ |
| **Sidecar duration vs samples** | **❌ 19.96 s declared, 19.48 s of samples: start stamped at segment open, ~0.5 s before the first sample (stream start-up). Breaks AC1 (≤ 33 ms).** |

## Fix and re-run

`AudioRecorder.stop_segment()` now returns the seconds actually written; `RecordCampaign` dates
the audio segment as `end − written`. Re-run (`qa2`): file 19.584 s, sidecar 19.584 s, **0.0 ms**
difference ✅. Unit tests 164 passed.

## Second fix (external review) and re-run

Anchoring the written duration on the tick's `now` could still drift if the tick or the drain is
slow. `stop_segment()` now returns the UTC times of the first and last sample, stamped in the
input callback. Re-run (`qa3`): file 19.637 s, sidecar 19.635 s, **−1.9 ms** (callback jitter,
well under AC1's 33 ms) ✅.

## Not covered

Camera path (Picamera2, ring flush, motion thread), real I²S levels, 7-day run, power draw.
