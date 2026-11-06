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
  OS on the microSD; time from NTP (the RTC battery is optional on the bench).
- Indoors, ambient 18–25 °C, recorded with each run; the board idle except for the run under test
  (the laptop runs showed that load skews latency, see
  [live-fps-laptop-cpu](../../research/live-fps-laptop-cpu.md)).
- Code from the head of `dev` being promoted; extras `capture`, `vision` and `train` installed.
- A bot token and chat ID for a test Telegram chat, held in the environment, never in a file
  under version control (ADR-0032).

## Acceptance criteria

Each row has an ID, a threshold, a procedure and the evidence to keep. A row that cannot run is
`BLOCKED` with the reason, never `PASS`.

### Capture

| AC | Threshold | Procedure | Evidence |
|---|---|---|---|
| **BA1** Camera stream | 1920×1080 at 30 fps; ≥ 99 % of the expected frames delivered over 10 min (≥ 17 820 of 18 000) | Start a campaign in the daylight window, wave a hand at 1 Hz in front of the lens for 10 min, count the frames from the clip timestamps | Frame count script output |
| **BA2** Audio stream | Both channels at 48 kHz / 24 bit; no ALSA overrun and no gap > 1 sample period in a 10-min segment; neither channel flat | Record one 10-min segment; check the sidecar, the FLAC header and the log; compare the RMS of both channels while tapping each mic | Sidecar, `soundfile` info, log excerpt |
| **BA3** Audio–video offset | ≤ 33 ms at the start and the end of a 10-min segment (capture-rig AC1) | Clap test at both ends of a segment; compare the clap frame time with the audio onset in each channel | Two frame grabs, two waveform plots, the four offsets |
| **BA4** Pixels on target | ≥ 30 px across a 30 mm object 10–50 cm in front of the camera (capture-rig AC6) | Ruler test with a 30 mm printed square at 10, 30 and 50 cm | Three frame grabs with the measured width |

### Recording

| AC | Threshold | Procedure | Evidence |
|---|---|---|---|
| **BA5** Pre-roll | ≥ 5 s before the first motion frame on 10 of 10 clips (capture-rig AC7) | Trigger 10 motion events ≥ 30 s apart; read each clip's first-motion offset | Table of 10 offsets |
| **BA6** Sidecars | 100 % of the segments and clips have every field of the capture-rig spec, `clock_source: ntp` (capture-rig AC3) | Run the sidecar check over every file of BA7 | Script output: files checked, files failing |
| **BA7** Unattended bench run | 72 h with no manual action; every daylight minute is covered by an audio segment, apart from the open segment at a restart | Start a campaign, leave it, then compare segment minutes with the expected daylight minutes | Segment count vs expected, log excerpt |
| **BA8** Disk budget | Daily volume within 13 GB ± 30 % (9–17 GB) on a day of BA7, with the motion share noted (ADR-0017 estimate) | `du` of one day's folder on the SSD | `du` output, motion minutes |
| **BA9** Disk full (A1) | Below 10 % free: oldest non-flagged segments are deleted and a fault is logged; below 2 % free: the rig enters *Fault* and stops (capture-rig AC8) | Fill the SSD with a placeholder file to each threshold during a campaign | Log excerpts, `df` before and after |
| **BA10** Power loss (A5) | After a pulled plug, recording resumes without manual action within 3 min of power-on; at most the open segment is lost (capture-rig AC8) | Pull the plug mid-segment, plug it back, wait | Log with the two timestamps, segment list |
| **BA11** Device loss (A2, A3) | A pulled mic or camera ribbon: the other streams go on, the fault is logged within 10 s, the camera is retried every second and comes back when re-plugged (capture-rig AC8) | Power off, unplug one mic, power on, record 2 min; then the same with the camera; re-plug the camera during the run | Log excerpts, sidecar gap fields |

Unplugging a ribbon or I²S wire on a powered Pi can damage it, so BA11 unplugs with the power off
and the failure is present from start. The mid-run camera case stays a unit test with fakes.

### Detection latency

Measured by the CLI's own figures (ADR-0030: warm-up apart, then p50 / p95 of `detect`, and FPS
end to end), with RF-DETR Small at the ACT threshold, on a clip recorded by the rig itself so the
run is repeatable.

| AC | Threshold | Procedure | Evidence |
|---|---|---|---|
| **BA12** Latency and throughput | p95 detect latency ≤ 500 ms and ≥ 2 FPS end to end on three runs of the same clip; warm-up ≤ 60 s | `aristech --video <clip.mp4> --detector rfdetr --checkpoint <path>` three times on the idle board | The three log lines (warm-up, FPS, p50, p95) |
| **BA13** Live source | The live camera opens and the same figures are logged after 10 min | `aristech --video 0 …` for 10 min (if OpenCV cannot open the camera directly, under `libcamerify`, noted) | Log lines |

**Why 500 ms / 2 FPS** — a hornet hovers in front of the entrance for seconds, and an episode opens
on 3 counted frames in a 10 s window (`alert` section of `config/config.yaml`): 2 FPS gives about
20 frames per window, enough to reach 3 hits on a real attack. A tighter target (≤ 200 ms, 5 FPS)
is what deterrence will need, and that is the accelerator's job in M6; a looser one (≤ 1 s, 1 FPS)
leaves only 10 frames per window. Totals and sensitivity:
[`mcda/spec_2026_11_06_bench_acceptance.py`](../../decisions/mcda/spec_2026_11_06_bench_acceptance.py)
(D2: C 455, A 425, B 425, measure only 260; C stays first when the achievability weight or the M6
weight rises). These are estimates: there is no Pi 5 measurement yet. If BA12 fails, open an issue
with the figures (smaller input, fewer threads, another runtime). Do not loosen the threshold
in place.

### Alert and health push

| AC | Threshold | Procedure | Evidence |
|---|---|---|---|
| **BA14** Attack alert | One push per episode, received ≤ 10 s after the frame that opens it; no push for a clip without hornets (attack-alert AC1, AC5) | Replay with `--push` a clip with a hornet episode, then a bees-only clip | Phone screenshot with time, log with the opening frame time |
| **BA15** Heartbeat | Received within ± 60 s of the period, set to 300 s for the test (health-push AC1, AC5) | Copy the config with `health.heartbeat_s: 300`, run 20 min with `--push` | Four messages with their times |
| **BA16** Fault push | A live camera that ends is pushed once as a fault; a second fault of the same kind in the cool-down is muted and counted (health-push AC3, AC4) | Run `--video 0 --push`, stop the camera stream twice inside the cool-down | One message, log with the muted count |
| **BA17** Channel down | With the network cut, detection goes on and the failure is logged; no secret appears in the log (attack-alert AC8, health-push AC6) | Pull the network during a BA14 replay | Log excerpt, `grep` for the token returns nothing |

### Power and heat

| AC | Threshold | Procedure | Evidence |
|---|---|---|---|
| **BA18** Power | Mean and peak power over 24 h of recording measured and recorded, as input to the solar sizing (capture-rig AC9); mean also measured for 1 h of detection | FNB58 between the supply and the Pi, logging to CSV | CSV and a summary in `docs/research/` |
| **BA19** Heat | SoC ≤ 80 °C and `vcgencmd get_throttled` = `0x0` after 1 h of recording and detection at the same time, with the case closed | Run `aristech-record` and, at the same time, the BA12 replay repeated in a shell loop for 1 h; sample `vcgencmd measure_temp` every minute | Temperature CSV, final `get_throttled` |
| **BA20** Supply | No under-voltage flag (bit 0 of `get_throttled`) during BA7, BA18 and BA19 | Read `get_throttled` at the end of each run | Three readings |

The Pi 5 starts to throttle at 85 °C; 80 °C keeps a margin for a summer day outdoors.

## Running a bench pass

1. Copy the [QA checklist template](../qa/checklist-template.md) to
   `docs/architecture/qa/<date>-bench-pi5.md`, level `full`, environment `staging, Pi`.
2. List BA1–BA20 as planned checks, run them, attach the evidence.
3. Commit the checklist and the BA18 summary; every FAIL becomes an issue.

## Alternative outcomes

- **A1 A threshold fails** → the row is FAIL, an issue is opened with the figures; the threshold
  changes only through a reviewed change of this spec.
- **A2 Hardware missing** (RTC battery out of stock) → rows that need it are `BLOCKED`; none of
  BA1–BA20 needs the RTC on the bench.

## Out of scope

Field criteria (capture-rig AC2, the 7-day run at the hive, and the outdoor enclosure), detection
accuracy (own-vision-model), the M6 accelerator and its latency target, solar sizing (after BA18).
