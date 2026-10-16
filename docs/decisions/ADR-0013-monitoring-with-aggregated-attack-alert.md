# ADR-0013: Monitoring with an aggregated attack alert

- Status: Accepted
- Date: 2026-10-16 (needs brainstorm, Q1)
- Supersedes: ADR-0006 (its observability model is kept; this ADR adds one aggregated alert)

## Context

ADR-0006 logs every detection locally and pushes only faults (plus a heartbeat watchdog), because a
push per detection is noise. The needs brainstorm asked what the beekeeper actually needs among
alert, count, deter and evidence. A log read after the fact tells the beekeeper an attack happened;
it does not let them react while it happens (fit an entrance reducer or muzzle, set a selective
trap, visit the apiary). Automatic deterrence stays gated by D0 (ADR-0005).

## Options (MCDA)

Criteria and weights: value to the beekeeper 30, legal / bee risk 25, feasibility now 25, data
collection 20. Scores 0–5.

| Option | C1 | C2 | C3 | C4 | Total /500 |
|---|---|---|---|---|---|
| A. Monitoring only: count, log, keep evidence | 3 | 5 | 5 | 5 | 440 |
| B. A + one aggregated "attack in progress" alert when hornet pressure crosses a threshold | 4 | 5 | 4 | 5 | **445** |
| C. A + automatic deterrence as the primary goal | 5 | 2 | 1 | 4 | 305 |

Sensitivity (script-checked): with value at 40 (feasibility 15), B 445, A 420; with feasibility at
35 (value 20), **A 460, B 445** — the choice flips if build effort outweighs the beekeeper's ability
to react. C stays last. **Chosen: B** (owner, 2026-10-16).

## Decision

- The product goal is **monitoring + an aggregated attack alert**:
  - **Count** hornets and record each detection in the structured local log (ADR-0006, unchanged).
  - **Keep evidence**: short clips / frames around detections, kept locally, for the beekeeper and
    for the training data flywheel.
  - **Alert** the beekeeper once per attack episode when the hornet pressure (counted
    *V. velutina* detections at the COUNT operating point, ADR-0014, over a sliding window) crosses
    a threshold; a cool-down prevents repeats. Threshold, window and cool-down are measured, not
    guessed, at the `attack-alert` gate.
- Still **no per-detection push**. Faults and heartbeat stay as in ADR-0006.
- Automatic deterrence remains a v2 consumer, gated by D0 (ADR-0005).

## Consequences

- New use case UC6 *Respond to an ongoing hornet attack* (actor: beekeeper); spec `attack-alert`.
- The push channel (Telegram / email) planned for faults in M6 also carries the attack alert, so
  the alert lands with or after M6, not before.
- Rejected: per-detection pushes (ADR-0006 option B), for the same signal-to-noise reason.
