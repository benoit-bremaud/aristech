# Local review — aristech (issue #149, COUNT point and attack episodes)

- Date: 2026-11-02
- Scope: branch diff `dev...feat/149-count-point-attack-alert`
- Checks run: `just gate` (lint, format, mypy, typos, actionlint, zizmor, tests, semgrep, osv,
  gitleaks, SonarQube) · code review of the diff (correctness, dependency rule, tests, docs)
- Verdict: ship · Must 0 · Should 4 (4 fixed) · Nice 7 (1 fixed)

## Pre-merge gate

| Step | Result |
|---|---|
| 1 Tests | ✅ 329 passed, 5 deselected (integration) |
| 2 Coverage | ✅ 97.86 % (floor 80) |
| 3 SonarQube | ✅ quality gate passed (13 new issues fixed: composite assertions, exception tests, cognitive complexity of `run`, `logging.exception`) |
| 4 Secrets | ✅ gitleaks clean · diff read: no checkpoint, video or secret committed |
| 5 QA pass | ✅ COUNT measured with the real checkpoint on test-v1: 0.15 (image P 0.800, R 0.96) ≤ ACT 0.45. CLI run on a 180-s sample clip from test-v1 images (10 s hornets, 70 s empty, ×2; sha256 `d8ca34cf…`): 2 alerts and 2 summaries; with 40-s gaps (< T): 1 alert |

## 🔴 Must Have
_None._

## 🟠 Should Have (fixed)
- An open episode got no summary when the run was interrupted or failed → closed in the `finally`, test added.
- The per-frame close path was not tested through the use case → two-episode test added.
- The exception path's alert behaviour was not pinned → test added.
- An empty or non-integer `alert.min_hit_frames` crashed or was truncated → validated, CLI tests added.

## 🟢 Nice to Have
- Fixed: the start alert logged a growing total as a window count → logs `peak`.
- Open: rebuild of the frozen episode on every frame (micro-cost); end time is the last frame, not
  the last pressure; `CAP_PROP_POS_MSEC` backend dependence; unreachable `"?"` fallback in the
  logger; COUNT sits on the precision target (re-measure on the field set, M5).
