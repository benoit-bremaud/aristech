# Spec — acceptance criteria for the C1 rig on the bench Pi 5

> **Status**: Proposed, criteria only (no code) · **Milestone**: C1, v1 stable · **Issue**: #171 ·
> **Related**: [capture-rig](capture-rig.md), [live-abstain](live-abstain.md),
> [attack-alert](attack-alert.md), [health-push](health-push.md), ADR-0017, ADR-0025, ADR-0030,
> ADR-0032, ADR-0033 · **Hardware**: [bench order list](../../research/2026-11-02-bench-order-list.md)

This spec lists the measurable criteria the bench Pi 5 must meet before the C1 rig goes outdoors
and before `v1.0.0` is cut: capture, recording, detection latency, alert and health push, power
and heat.

## Need

The bench Pi 5 is both the first C1 unit (ADR-0017) and the staging device of the promotion model
(ADR-0025). The specs it runs define their behaviour and unit-test it with fakes; none of them says
what "works on the real board" means. This spec fills that gap with numbers and procedures, so a
bench pass is a list of PASS / FAIL rows, not an opinion. It also sets the detection latency target
that [`requirements.md`](../../requirements.md) left "to be defined", for the Pi 5 CPU only. The
embedded accelerator (M6) gets its own target later.

The criteria refer to the feature specs and do not restate them. Where a feature AC already holds
the threshold, the bench row points to it and adds only the bench procedure.

## Actors

| Actor | Kind | Goal |
|---|---|---|
| **Researcher** | primary, human | Assemble the bench, run each procedure, record the evidence. |
| **Owner as QA** | primary, human | Read the evidence and sign the bench pass (QA checklist, #134). |
| **Telegram** | secondary, system | Receive the pushes (ADR-0032). |

## Preconditions

- Bench assembled per the [order list](../../research/2026-11-02-bench-order-list.md): Pi 5 8 GB,
  27 W supply, active cooler, Camera Module 3, 2 × ICS-43434 on I²S, 512 GB NVMe on the M.2 HAT+,
  OS on the microSD, no enclosure; time from NTP (the RTC battery is optional on the bench).
- Indoors, ambient 18–25 °C, recorded with each run; the board idle except for the run under test
  (the laptop runs showed that load skews latency, see
  [live-fps-laptop-cpu](../../research/live-fps-laptop-cpu.md)).
- Code from the head of `dev` being promoted, run from the repository root (the default
  `config/config.yaml` path is relative); extras `capture`, `vision` and `train` installed.
- Runs that need the camera stop `aristech-record` first: the camera has one owner at a time.
- A spare USB webcam for BA16 (not in the BOM; BA16 is `BLOCKED` without it).
- A bot token and chat ID for a test Telegram chat, held in the environment, never in a file
  under version control (ADR-0032).
- The board is rebooted before each run that reads `vcgencmd get_throttled`, so the "since boot"
  flags belong to that run.

## Acceptance criteria

Each row has an ID, a threshold, a procedure and the evidence to keep. A row that cannot run is
`BLOCKED` with the reason, never `PASS`. A row marked *needs a follow-up* is `BLOCKED` until the
named follow-up exists.

### Capture

| AC | Threshold | Procedure | Evidence |
|---|---|---|---|
| **BA1** Camera stream | Clips at 1920×1080, 30 fps; each clip holds ≥ 99 % of `duration × 30` frames | In the daylight window, wave a hand at 1 Hz in front of the lens for 10 min (clips are capped at 5 min, so expect several); count the frames of each clip with `ffprobe -count_frames` | Per-clip table: duration, expected, counted |
| **BA2** Audio stream | Both channels at 48 kHz / 24 bit; per 10-min segment, FLAC frame count within ± 4 096 samples (≈ 85 ms) of `(end_utc − start_utc) × 48 000`; neither channel flat | Record one segment while tapping each mic in turn; read the FLAC header and the sidecar; compare both channels' RMS | `soundfile` info, frame-count check, RMS of both channels |
| **BA3** Audio–video offset | ≤ 33 ms at the start and the end of a 10-min segment (capture-rig AC1) | Clap test at both ends of a segment; compare the clap frame time with the audio onset in each channel | Two frame grabs, two waveform plots, the four offsets |
| **BA4** Pixels on target | ≥ 30 px across a 30 mm object 10–50 cm in front of the camera (capture-rig AC6) | Ruler test with a 30 mm printed square at 10, 30 and 50 cm | Three frame grabs with the measured width |

### Recording

| AC | Threshold | Procedure | Evidence |
|---|---|---|---|
| **BA5** Pre-roll | ≥ 5 s between a clip's first frame and the first frame showing motion, on 10 of 10 clips (capture-rig AC7) | Film a running stopwatch, then trigger 10 motion events ≥ 30 s apart; find the first frame where the motion shows, by eye or frame by frame, and read the offset from the clip start (the sidecar `start_utc` is set from the pre-roll, so reading it would prove nothing) | Table of 10 offsets |
| **BA6** Sidecars | Every segment and clip has the keys of `SegmentMetadata.to_dict` (`rig_id`, `hive_id`, `site`, `kind`, `trigger`, `start_utc`, `end_utc`, `clock_source`, `software_version`, `settings`, `missing_inputs`, `flagged`); `clock_source` is `ntp`, except the first segment after a boot, which may be `rtc` (capture-rig AC3) | Run the key check over every file of BA7, or of a run of at least one day started by hand while BA7 is blocked | Script output: files checked, files failing |
| **BA7** Unattended bench run | 72 h with no manual action; every daylight minute is covered by an audio segment, apart from the open segment at a restart | Start a campaign as a service, leave it, then compare segment minutes with the expected daylight minutes. *Needs a follow-up*: a service unit that starts `aristech-record` at boot and restarts it on exit | Segment count vs expected, log excerpt |
| **BA8** Disk rates | Audio within ± 30 % of 0.5 GB per daylight hour (ADR-0017: ~6 GB per 12 h for two channels); video within ± 30 % of 3.6 GB per motion hour (~8 Mbit/s). The 13 GB/day of ADR-0017 is then re-derived from the measured rates and the field motion time | On one day of BA7 (or of the hand-started run of BA6), `du` the audio and the video folders; sum the daylight hours and the clip durations | `du` output, hours, the two rates |
| **BA9** Disk full (A1) | Below 10 % free: the oldest non-flagged segments are deleted and a fault is logged; below 2 % free: the rig enters *Fault* and stops (capture-rig AC8) | Run last, after the BA6–BA8 evidence is copied off: every non-flagged segment on the target will be deleted. Point `--output` at a small dedicated filesystem (a 2 GB loop file) and fill it with a placeholder file to each threshold during a campaign | Log excerpts, `df` before and after |
| **BA10** Power loss (A5) | After a pulled plug, recording resumes without manual action within 3 min of power-on; at most the open segment is lost (capture-rig AC8). *Needs a follow-up*: the service unit of BA7 | Pull the plug mid-segment, plug it back, wait | Log with the two timestamps, segment list |
| **BA11** Device absent at start (A2, A3) | With one mic, then the camera, disconnected before power-on: the other streams record, the missing input is logged and written in `missing_inputs` (capture-rig AC8) | Power off, disconnect one mic, power on, record 2 min; power off, reconnect; repeat with the camera ribbon | Log excerpts, sidecars |

Unplugging a ribbon or an I²S wire on a powered Pi can damage it, so BA11 changes wiring with the
power off only. A device lost mid-run and the camera retry every second stay covered by the unit
tests with fakes (capture-rig AC8); the retry logs only at DEBUG, so a bench run would not show it.

### Detection latency

Measured by the CLI's own `Timing:` line (ADR-0030: the warm-up apart, then p50 / p95 of `detect`,
and FPS end to end), with RF-DETR Small at the ACT threshold, on a clip recorded by the rig itself
so the run is repeatable.

| AC | Threshold | Procedure | Evidence |
|---|---|---|---|
| **BA12** Latency and throughput | On each of three runs of the same clip: p95 detect latency ≤ 500 ms, ≥ 2 FPS end to end, warm-up ≤ 60 s | `aristech --video <clip.mp4> --detector rfdetr --checkpoint <path>`, three times on the idle board | The three `Timing:` lines |
| **BA13** Live source | The live camera opens and the same thresholds hold over 10 min | Stop `aristech-record`; run `aristech --video 0 --detector rfdetr --checkpoint <path>` (under `libcamerify` if OpenCV cannot open the camera directly, noted); press Ctrl-C after 10 min | The `Timing:` line |

**Why 500 ms / 2 FPS** — a hornet hovers in front of the entrance for seconds, and an episode opens
on 3 counted frames in a 10 s window (`alert` section of `config/config.yaml`): 2 FPS gives about
20 frames per window, enough to reach 3 hits on a real attack. A tighter target (≤ 200 ms, 5 FPS)
is what deterrence will need, and that is the accelerator's job in M6; a looser one (≤ 1 s, 1 FPS)
leaves only 10 frames per window. Totals and sensitivity:
[`mcda/spec_2026_11_06_bench_acceptance.py`](../../decisions/mcda/spec_2026_11_06_bench_acceptance.py)
(D1, where these criteria live: a new spec 435, a section in capture-rig 340, spread over four
specs 325; D2: C 455, A 425, B 425, measure only 260). C stays first when the achievability or
the M6 weight rises, but only by 5 points (445 vs 440), and the achievability scores are estimates:
there is no Pi 5 measurement yet. If BA12 fails, open an issue with the figures (smaller input,
fewer threads, another runtime). Do not loosen the threshold in place.

### Alert and health push

| AC | Threshold | Procedure | Evidence |
|---|---|---|---|
| **BA14** Attack alert | Exactly one alert and one summary per episode; the alert reaches the phone ≤ 10 s after the wall-clock time of the "attack started" log line; no push for a bees-only clip (attack-alert AC1, AC2) | Replay with `--push telegram` the 80-s sample clip of the #149/#152 verification (rebuilt from test-v1 images, recipe in [attack-alert](attack-alert.md)), then a bees-only clip. On a replay, frame times follow the video, not the wall clock, so the delay is measured from the log line's time stamp | Phone screenshot with times, log excerpt |
| **BA15** Heartbeat | Four heartbeats in 21 min, each within ± 60 s of `start + k × 300 s` (health-push AC1, AC5) | Copy the config with `health.heartbeat_s: 300`; `aristech --config <copy> --video 0 --detector rfdetr --checkpoint <path> --push telegram` for 21 min | Four messages with their times |
| **BA16** Fault push | The end of the live source is pushed once as a `source_ended` fault (health-push AC3) | Run BA15's command with a spare USB webcam (any model) as `--video <n>`, `<n>` being its index from `v4l2-ctl --list-devices`, instead of the Camera Module 3, and unplug its USB cable, which is safe while powered (a CSI ribbon is not; Ctrl-C does not count, it ends the run without a fault). The mute and count of repeated faults (health-push AC4) needs two faults in one process and stays covered by `test_health.py` | One message, log excerpt |
| **BA17** Channel down | With the network cut, detection goes on and the failure is logged; the bot token never appears in the log (attack-alert AC8, health-push AC6) | Pull the network during a BA14 replay; `grep` the log for the token | Log excerpt, empty `grep` |

### Power and heat

| AC | Threshold | Procedure | Evidence |
|---|---|---|---|
| **BA18** Power | Mean and peak power over 24 h of recording measured and recorded, as input to the solar sizing (capture-rig AC9); mean also measured for 1 h of detection | FNB58 between the supply and the Pi, logging to CSV; check with `vcgencmd get_config usb_max_current_enable` that the meter keeps the 5 A negotiation | CSV and a summary in `docs/research/` |
| **BA19** Heat | SoC ≤ 75 °C and no throttling flag (`get_throttled` bits 1–3 and 17–19 clear) after 1 h of recording and detection at the same time, bare board with the active cooler | Inside the daylight window with the rig in *Recording*: run `aristech-record` and, at the same time, the BA12 replay repeated in a shell loop for 1 h; sample `vcgencmd measure_temp` every minute | Temperature CSV, final `get_throttled` |
| **BA20** Supply | No under-voltage since boot (`get_throttled` bit 16 clear) at the end of BA7, BA18 and BA19 | Read `get_throttled` at the end of each run, after the reboot of the preconditions | Three readings |

The Pi 5 firmware starts to throttle the CPU from about 80 °C and throttles harder at 85 °C; 75 °C
keeps a margin for the closed enclosure and a summer day outdoors.

## Running a bench pass

1. Copy the [QA checklist template](../qa/checklist-template.md) to
   `docs/architecture/qa/<date>-bench-pi5.md`, level `full`, environment `staging, Pi`.
2. List BA1–BA20 as planned checks, run them, attach the evidence.
3. Commit the checklist and the BA18 summary; every FAIL becomes an issue.

## Follow-ups this spec needs

- A service unit that starts `aristech-record` at boot and restarts it on exit (BA7, BA10).
- The motion check runs once per second, so the pre-roll before the first motion frame may be
  shorter than 5 s; BA5 is expected to show it, and a fix (a longer ring or a faster check) follows
  the measurement.

## Alternative outcomes

- **A1 A threshold fails** → the row is FAIL, an issue is opened with the figures; the threshold
  changes only through a reviewed change of this spec.
- **A2 Hardware missing** (RTC battery out of stock) → rows that need it are `BLOCKED`; none of
  BA1–BA20 needs the RTC on the bench.

## Out of scope

Field criteria (capture-rig AC2, the 7-day run at the hive, and the outdoor enclosure), detection
accuracy (own-vision-model), the M6 accelerator and its latency target, solar sizing (after BA18).
