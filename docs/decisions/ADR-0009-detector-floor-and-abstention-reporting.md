# ADR-0009: Separate detector floor from operating threshold; report abstentions

- Status: Accepted
- Date: 2026-10-16 (brick B4, owner-validated weights and options)

## Context

ADR-0004 sets one operating threshold `c` for ACT vs ABSTAIN. The CLI also configured the detector
at `c`, so every box below `c` was dropped before `decide()` and ABSTAIN never fired live
(audit M3). In addition, `DetectHornetVisual` only reported ACT, so even a reachable ABSTAIN would
stay invisible (ADR-0006 asks for observability). Two choices follow. Spec:
`docs/architecture/specs/live-abstain.md`.

## Decision 1 — detector floor

Criteria and weights: legal floor / correctness 40, simplicity 30, CPU cost 30. Scores 0–5.

| Option | C1 | C2 | C3 | Total /500 |
|---|---|---|---|---|
| A. New `--detector-floor` flag (default 0.1, must be `<= --confidence`); `--confidence` stays the operating threshold | 5 | 4 | 4 | **440** |
| B. Detector always at 0.0 | 5 | 5 | 2 | 410 |
| C. Floor derived as `c / 2` | 4 | 3 | 4 | 370 |

Sensitivity: B overtakes A only if CPU cost weighs under 15. **Chosen: A.**

## Decision 2 — abstention visibility

Criteria and weights: observability (ADR-0006) 40, port discipline 30, testability 30.

| Option | C1 | C2 | C3 | Total /500 |
|---|---|---|---|---|
| A. `Notifier.notify_abstention(detection)`; `LoggingNotifier` logs it at INFO | 5 | 4 | 5 | **470** |
| B. The use case logs directly | 3 | 4 | 2 | 300 |
| C. `run()` also returns abstentions, the CLI logs them | 4 | 3 | 4 | 370 |

Robust to any reasonable weight change. **Chosen: A.** The port gains a method; its only
implementation and the test fake are updated together.

## Consequences

- `--confidence` keeps its meaning for users (operating threshold); the detector floor is new.
- `DetectHornetVisual.run()` returns a result with threats and abstentions, so the CLI can count both.
- Every future `Notifier` adapter must handle abstentions (may be a no-op).
- Supersedes nothing; closes the "known gap" consequence of ADR-0004.
