# Local review — aristech (branch `docs/132-bench-pi5-order-list`)

- Date: 2026-11-02
- Scope: branch diff `dev...HEAD` (bench order list, storage MCDA script, this report)
- Checks run: docs · correctness (prices against live pages, totals, MCDA arithmetic) · security
- Verdict: **ship** · Must 0 · Should 0 · Nice 2

## Pre-merge gate

| Step | Result |
|---|---|
| 1 Tests | ✅ `mise x -- just check` green (no product code changed) |
| 2 Coverage | no `src/` change; the MCDA script mirrors the existing `mcda/` scripts and has docstrings |
| 3 SonarQube | `just gate` before merge |
| 4 Secrets | gitleaks in `just check`; diff read: public URLs only |
| 5 QA pass | no UI: MCDA script run, totals match the note (390 / 380 / 375 / 345, flip at capacity 35); BOM total recomputed by script (666.32 EUR, Kubii subtotal 452.80 EUR) |

## 🔴 Must Have

_None._

## 🟡 Should Have

_None._

## 🔵 Nice to Have

- Prices and stock are snapshots from 2026-11-02 · re-check at order time.
- Two lines unpriced (RTC battery out of stock, insect mesh not verifiable online) · stated in
  the note and excluded from the total.

## ⚪ Disagree / Intentional

- ADR-0017 is not superseded: the decision (NVMe on M.2 HAT+) holds; only the bench unit's SSD
  capacity changes, recorded in the research note with its own MCDA.
