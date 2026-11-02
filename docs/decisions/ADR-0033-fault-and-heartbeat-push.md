# ADR-0033: Fault and heartbeat pushes on the alert channel

- Status: Accepted
- Date: 2026-11-02 (issue #158)
- Complements: ADR-0006 (heartbeat and faults), ADR-0032 (Telegram push channel)

## Context

A unit at a remote apiary that dies stays silent. ADR-0006 asks for a heartbeat and for pushes of
the faults the unit can detect and still deliver; ADR-0032 built a push channel for the attack
alert. No server-side watchdog exists yet (M6), so the heartbeat goes to the beekeeper on the same
channel: a missing heartbeat is the dead man's switch. Three choices: the heartbeat period, the
faults covered, and how faults are rate-limited.

## Options (MCDA)

Scores 0–5; totals and sensitivity computed by `mcda/adr_0033_fault_heartbeat.py` (every weight
vector in steps of 5).

### Heartbeat period

Criteria and weights: liveness latency 35, noise 35, battery and data 15, simplicity 15.

| Option | Latency | Noise | Battery | Simplicity | Total /500 |
|---|---|---|---|---|---|
| A. Hourly | 5 | 1 | 2 | 5 | 315 |
| B. Every 6 h | 4 | 3 | 4 | 5 | 380 |
| C. Daily (24 h) | 2 | 5 | 5 | 5 | **395** |

Sensitivity: C first in 67 % of weight vectors, B 23 %, A 14 %. B passes C when latency weighs 45
or noise 25. The period is a configuration value (`health.heartbeat_s`).

### Faults covered

Criteria and weights: coverage of silent deaths 40, false alarms 20, feasible without the Pi 20,
simplicity 20.

| Option | Coverage | False alarms | Feasible | Simplicity | Total /500 |
|---|---|---|---|---|---|
| A. Detection loop error only | 2 | 5 | 5 | 5 | 380 |
| B. Loop error + live source ended | 4 | 5 | 5 | 4 | **440** |
| C. B + disk, temperature, battery | 5 | 3 | 1 | 2 | 320 |

Sensitivity: B first in 64 % of weight vectors and at ±10 on every criterion. C waits for the
embedded hardware (M6).

### Rate limiting

Criteria and weights: no flood 35, no lost fault 30, simplicity 20, testability 15.

| Option | No flood | No loss | Simplicity | Testability | Total /500 |
|---|---|---|---|---|---|
| A. None | 1 | 5 | 5 | 5 | 360 |
| B. One push per fault kind per cool-down (1 h) | 5 | 4 | 4 | 5 | **450** |
| C. Global token bucket | 4 | 3 | 2 | 3 | 315 |

Sensitivity: B first in 63 % of weight vectors and at ±10 on every criterion. **Chosen: C, B, B**
(owner, 2026-11-02).

## Decision

- `application/health.py`: `HealthMonitor` (pure, wall `Clock` injected) says when a heartbeat is
  due and which faults pass the per-kind cool-down; muted faults are counted and reported with the
  next push. Defaults 24 h and 1 h, set in the `health` section of `config/config.yaml`.
- `Notifier` gains `notify_heartbeat` and `notify_fault`; `LoggingNotifier` logs them (fault at
  ERROR) and `TelegramNotifier` pushes them through the same queue (ADR-0032 A1, A3). No new port.
- `DetectHornetVisual` ticks the monitor once per frame, reports an exception as `loop_error`
  before raising it, and the end of a live (camera) source as `source_ended`. The end of a video
  file is normal. An operator interrupt (Ctrl-C) is not a fault.
- The pushed fault carries its kind and time, never the exception text, which can hold paths.

## Consequences

- A camera that blocks without raising sends neither a fault nor a heartbeat: the missing
  heartbeat reveals it. A thread watchdog, the server-side watchdog and hardware faults come with
  M6.
- The heartbeat is tied to the loop: it proves frames are processed, not only that the process
  runs.
- The rate limit lives in the process: each fault ends the run, so a service manager that restarts
  the unit at once sends one fault per restart. Set the restart delay to at least the cool-down
  (`RestartSec` with systemd, M6), or persist the last fault time if that proves too noisy.
- Only a camera index counts as a live source; a network stream URL is handled as a file, so its
  end is not a fault yet (add when a network camera is used).
- A push channel failure cannot be pushed; it stays in the log and the delayed queue (ADR-0032).
- The beekeeper learns of a dead unit up to 24 h late; lower `heartbeat_s` if that is too long.
