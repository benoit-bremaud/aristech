# Pre-push review — fix/111-bump-vulnerable-vision-pins

Review of the Python 3.11 floor and the vision-pin bump (ADR-0026, issue #111) before the push.

- Date: 2026-10-30
- Commit: a7bcf48
- Scope: branch diff `origin/dev...HEAD` (29 files)
- Verdict: ship as-is · Must 0 · Should 0 · Nice 1

## Pre-merge gate

| Step | Result |
|---|---|
| 1 Tests | ✅ 270 unit passed on 3.11 (5 deselected integration); real-weights check below |
| 2 Coverage | tests 98 % statements (floor 80) |
| 3 SonarQube | ✅ PASSED (local scan of the branch head, new coverage 98.3 %, duplication 0 %) |
| 4 Secrets | ✅ gitleaks clean on `origin/dev..HEAD` · only `.env.example` tracked · diff read: nothing sensitive |
| 5 QA pass | ✅ real-weights run (below), no UI in scope |

Static: `ruff check` and `ruff format --check` on `src tests` clean, `mypy src` clean,
`osv-scanner` on `requirements.txt`: no issues.

Real-weights check (ADR-0026 § Consequences): fresh Python 3.11 venv with the new lock (Pillow
13.0.0, torch 2.14.1 + CUDA), `make prefield-report` with the VespAI weights and the RF-DETR
checkpoint: `docs/research/prefield-model-test-v1-tables.md` reproduced byte for byte.

## 🔴 Must Have

_None._

## 🟡 Should Have

_None._

## 🔵 Nice to Have

- `docs/INSTALL.md:45` `[docs]` · the training venv also needed `typing_extensions` newer than the
  lock's 4.12.0 (rfdetr's dependency tree imports `Sentinel`) · track with the train extra in #109.

## ⚪ Disagree / Intentional

- `docs/research/m3-vespai-baseline-requirements.txt` `[security]` · still flagged by osv · frozen
  record of a past run (ADR-0026); excluded from the scan in #109.
- Unformatted files under `notebooks/`, `scripts/`, `docs/architecture/qa/tools/` · outside the
  `src tests` scope of CI and untouched by this diff.
