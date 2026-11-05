# Pre-push review — feat/158-fault-heartbeat-push

Review of the diff against `dev` (issue #158, ADR-0033) before the first push.

## Checks

- `just gate`: green (364 tests, coverage 98 %, SonarQube quality gate passed after one test fix).
- Design, correctness, tests and docs read by an independent reviewer pass.

## Findings

| # | Priority | Finding | Resolution |
|---|---|---|---|
| 1 | Should | Fault rate limit is per process; a crash-restart loop pushes one fault per restart | Documented in ADR-0033 and spec A3: restart delay ≥ cool-down; persistence if needed |
| 2 | Should | `source_ended` sent inside the `try`: a failing push would also be reported as `loop_error` | Fixed: sent after the `try` block |
| 3 | Should | A network stream URL is not treated as a live source | Documented as a known limit (ADR-0033, spec A2) |
| 4 | Nice | A raising `notify_fault` in the `except` hides the original error behind chaining | Not done: both adapters never raise (ADR-0032 A3) |
| 5 | Nice | Make "hung source sends no heartbeat" explicit | Fixed: `tick` docstring |
| 6 | Nice | Push the exception type for mobile diagnosis | Not done: kind is enough for the beekeeper; detail stays in the log |

No Must Have finding.
