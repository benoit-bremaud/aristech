# Local review — aristech (M4 operating point, issue #18)

- Date: 2026-11-02
- Scope: branch diff `dev...feat/18-operating-point-threshold` (spec `operating-point`, AC1–AC6)
- Checks run: correctness · tests · security (gitleaks + diff read) · design/docs proportional
- Verdict: ship · Must 0 · Should 1 (1 fixed) · Nice 2

## Pre-merge gate

| Step | Result |
|---|---|
| 1 Tests | ✅ `just gate`: 284 passed (3.11 and 3.12 runs), ruff, mypy, typos, semgrep clean |
| 2 Coverage | ✅ 96 % (floor 80); new code 98.3 % |
| 3 SonarQube | ✅ quality gate passed |
| 4 Secrets | ✅ gitleaks: no leaks · diff read: no secrets, no weights or images committed |
| 5 QA pass | ✅ [`qa/2026-11-02-operating-point.md`](../qa/2026-11-02-operating-point.md) |

## 🔴 Must Have
_None._

## 🟡 Should Have
- `tests/unit/evaluation/test_operating_point.py` `[tests]` · SonarQube S5778, two calls inside
  `pytest.raises` · **Fixed**: samples built before the block.

## 🟢 Nice to Have
- `operating_point.py` `[perf]` · `false_alert_rate` re-scans the samples per threshold; 19 × 288
  images is instant, revisit only for large field sets.
- `docs/research/operating-point-test-v1.md` `[docs]` · no PNG curve (avoids a matplotlib
  dependency); the tables carry the same data.
