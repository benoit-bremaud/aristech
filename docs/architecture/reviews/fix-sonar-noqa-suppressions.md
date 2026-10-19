# Pre-push review — fix/sonar-noqa-suppressions

Date: 2026-10-19

## Scope

SonarQube gate red on `main`: `new_violations = 4`, rule python:S7632 (malformed issue
suppression comment) on the `# noqa: BLE001 — <reason>` comments in
`infrastructure/capture/picamera2_recorder.py` and `sounddevice_recorder.py`.

## Change

The ruff config selects `E, F, I, B, UP`; `BLE` is not enabled, so the seven
`# noqa: BLE001` markers suppressed nothing. They are replaced by plain `# <reason>`
comments (all seven, not only the four flagged, for consistency). No behaviour change.

## Checks

| Check | Result |
|---|---|
| `make lint` (ruff check + format --check) | pass |
| `make type-check` (mypy strict) | pass |
| `make test-unit` | 164 passed, 2 skipped (cv2 absent) |
| `make sonar` → quality gate | **OK** — new_violations 0, new_coverage 97.5 %, duplication 0 % |
| Secrets / manual diff read | comment-only diff, nothing sensitive |
| QA on running product | n/a — comment-only change |

## Findings

Must: none. Should: none. Nice: none.
