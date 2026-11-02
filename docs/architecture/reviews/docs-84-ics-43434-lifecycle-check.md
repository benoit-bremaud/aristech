# Local review — aristech (branch `docs/84-ics-43434-lifecycle-check`)

- Date: 2026-11-02
- Scope: branch diff `dev...HEAD` (research note, MCDA script, this report)
- Checks run: docs · correctness (sources, MCDA arithmetic) · security
- Verdict: **ship** · Must 0 · Should 0 · Nice 1

## Pre-merge gate

| Step | Result |
|---|---|
| 1 Tests | ✅ `mise x -- just check` green (no product code changed) |
| 2 Coverage | no `src/` change; the MCDA script mirrors the existing `mcda/` scripts and has docstrings |
| 3 SonarQube | `just gate` before merge |
| 4 Secrets | gitleaks in `just check`; diff read: public URLs only |
| 5 QA pass | no UI: MCDA script run, totals match the note (410 / 330 / 285, flip at longevity 35) |

## 🔴 Must Have

_None._

## 🟡 Should Have

_None._

## 🔵 Nice to Have

- Stock figures are snapshots from 2026-11-02 · re-check at order time (stated in the note).

## ⚪ Disagree / Intentional

- ADR-0017 is not edited (accepted ADRs are immutable); the BOM delta (+2 spare breakouts) is
  recorded in the research note and applied by the bench order issue.
