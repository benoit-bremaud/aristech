# ADR-0006: Observability model instead of per-detection alerts

- Status: Superseded by ADR-0013 (model kept, one aggregated attack alert added)
- Date: 2026-05-22 (PR #26)

> Retroactive ADR (written 2026-10-16, brick B1). The decision predates the ADR practice;
> the MCDA scores are reconstructed from the rationale recorded at the time and were not
> owner-weighted then. Source of truth for the original wording: the cited PRs and `PROJECT_LOG.md`.

## Context

The device is autonomous, unattended and outdoors. Pushing a notification per detection floods
the owner and says nothing about whether the device is alive.

## Options (MCDA)

Criteria and weights (C1…): signal-to-noise 35, liveness detection 35, simplicity 30. Scores 0–5.

| Option | C1 | C2 | C3 | Total /500 |
|---|---|---|---|---|
| A. Detections to a structured local log, heartbeat + server watchdog, push only on faults | 5 | 5 | 3 | 440 |
| B. Push every detection (aggregated) | 1 | 1 | 5 | 220 |
| C. Local log only | 4 | 0 | 5 | 290 |

## Decision

Option A. v1 implements the structured detection log (`LoggingNotifier`); heartbeat, fault
alerting and the watchdog come with the embedded deployment (M6).

## Consequences

- The `Notifier` port carries detection events to the log, not to a push channel.
