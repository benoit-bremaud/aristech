# Local review — aristech (branch `research/m3-vespai-baseline`)

- Date: 2026-10-19
- Scope: branch diff `main...HEAD` (script, Makefile target, tests, spec, gate, report)
- Checks run: design · docs · tests · security · correctness
- Verdict: **ship after the fixes below (applied)** · Must 0 · Should 6 (fixed) · Nice 4

## Pre-merge gate

| Step | Result |
|---|---|
| 1 Tests | ✅ 177 unit · integration: VespAI test skipped (no torch in the dev venv), 4 `tests/config/test_env_vars.py` fail without a local `.env` (pre-existing, unrelated) · real VespAI run done in step 5 |
| 2 Coverage | tests 97 % (`aristech`), new script 96 % (`scripts/vespai_baseline_report.py`) · docs: every new public function has a docstring |
| 3 SonarQube | ❌ gate ERROR: `new_violations` = 4, all `python:S7632` (malformed suppression comments) in `infrastructure/capture/*_recorder.py`, already on `main` since PR #86 — none in this diff; new coverage 97.5 %, duplication 0 % |
| 4 Secrets | ✅ gitleaks clean (`main..HEAD`) · only `.env.example` tracked · diff read: hashes and public URLs only, no weights, dataset or images committed |
| 5 QA pass | ✅ no UI: the documented `make m3-report` command run on the real weights and dataset; output identical to the report, three runs identical, no NMS warning — `docs/architecture/qa/2026-10-19-m3-report.txt` |

- Gate: **RED on step 3 only, caused by `main`** — fix in a separate branch, or owner exception.

## 🔴 Must Have

_None._

## 🟡 Should Have (all fixed in this branch)

- `Makefile` m3-report `[security|correctness]` · paths expanded unquoted by the shell; bare `python` · values exported and quoted (`"$$WEIGHTS"`), `PYTHON ?= python`.
- `scripts/vespai_baseline_report.py` split check `[correctness]` · a `FileNotFoundError` from torch would be reported as a missing split · splits checked up front, before the detector is built; the catch is removed.
- `tests/unit/scripts/test_vespai_baseline_report.py` `[tests]` · A1 covered only for the dataset · parametrized over dataset / weights / YOLOv5 dir, asserting the message and no detector call.
- same file `[tests]` · missing-split test asserted the exit code only · asserts the message and that the detector is never built.
- same file `[tests]` · AC3 defaults not pinned · test for the default splits, IoU and class map (class 0 = crabro).
- `docs/research/m3-vespai-baseline.md` known limits `[docs|correctness]` · "floor does not change the tables" overstated · states the `>` vs `>=` edge at exactly 0.500 and that no NMS warning was logged at 0.5.

## 🔵 Nice to Have

- `scripts/vespai_baseline_report.py:43` `[design]` · class-map parser duplicated from `measure_operating_point.py` minus the target check · kept: two copies with deliberately different rules (rule of three).
- `Makefile` `[design]` · `ruff`/`mypy` in CI cover `src tests` only, so `scripts/` is not linted by CI (pre-existing) · checked by hand for this script; follow-up.
- `.gitignore` `[docs]` · `data/external/` is already covered by `data/**` · kept as an explicit, documented location.
- `docs/research/m3-vespai-baseline.md` reproduce step 2 `[security]` · `unsafe-best-match` with an extra index · annotated: the extra index serves torch only.

## ⚪ Disagree / Intentional

- `scripts/vespai_baseline_report.py` `DetectorFactory` `[design]` · a callable seam, not a port; its force is the unit-test fake (CLAUDE.md).

## Per-dimension summary

- Design: dependency rule kept, VespAI imported lazily, no over-engineering. · Docs: spec, gate,
  report and code agree (AC1–AC6). · Tests: hand-written fake at the port, A1–A3 and AC2–AC3
  covered. · Security: no secrets, weights by SHA-256, pickle loaded only from a trusted path. ·
  Correctness: table arithmetic checks out (1343 velutina + 607 crabro = 1950 boxes).
