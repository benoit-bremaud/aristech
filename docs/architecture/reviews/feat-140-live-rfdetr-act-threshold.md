# Local review — aristech (issue #140, live RF-DETR at the ACT threshold)

- Date: 2026-11-02
- Scope: branch diff `dev...feat/140-live-rfdetr-act-threshold`
- Checks run: `just gate` (lint, format, mypy, typos, actionlint, zizmor, tests, semgrep, osv,
  gitleaks, SonarQube) · code review of the diff (correctness, dependency rule, tests, docs)
- Verdict: ship · Must 0 · Should 3 (3 fixed) · Nice 3 (1 fixed)

## Pre-merge gate

| Step | Result |
|---|---|
| 1 Tests | ✅ 295 passed, 5 deselected (integration) |
| 2 Coverage | ✅ 80%
97.84% (floor 80); new code 98 % on SonarQube |
| 3 SonarQube | ✅ quality gate passed (one cognitive-complexity issue fixed by splitting the model checks) |
| 4 Secrets | ✅ gitleaks clean · diff read: no checkpoint, no secret, only the public sha256 |
| 5 QA pass | ✅ CLI run end to end with the real checkpoint on a 60-frame sample video: no sha warning, 16 ACT, 48 ABSTAIN, timing logged (`docs/research/live-fps-laptop-cpu.md`) |

## 🔴 Must Have
_None._

## 🟠 Should Have (fixed)
- `--detector` help did not say RF-DETR needs the `train` extra → added.
- Timing was not logged when detection raised → `_log_timing` in a `finally`, test added.
- RF-DETR tests sliced the fixture argv by position → explicit base argv.

## 🟢 Nice to Have
- Fixed: the MCDA script is committed (`docs/decisions/mcda/adr_0030_live_default_threshold.py`).
- Open: the sha warning wording when `--confidence` is set on purpose; a use-case-level test of
  the IGNORE debug log (covered through the CLI test).
