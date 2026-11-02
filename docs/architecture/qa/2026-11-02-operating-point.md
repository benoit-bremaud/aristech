# QA checklist — operating point (issue #18)

| Date | Head SHA | Level | Environment | Branch / PR |
|---|---|---|---|---|
| 2026-11-02 | 028b0db + staged diff | pass | local, laptop (CPU) | feat/18-operating-point-threshold |

## 1. Coverage

- [x] [`traceability/matrix.md`](../traceability/matrix.md) is up to date with the diff (UC4 row:
      activity diagram, ADR-0029).
- [x] Every row below has at least one planned check, or a reason why none applies.

| Use case / requirement | What the diff changes | Planned checks |
|---|---|---|
| UC4 Select the operating points | margin, false-alert cap, bound; RF-DETR in the script | QA-01, QA-02, QA-03 |
| requirements § Operating point | provisional ACT value 0.45 | QA-02 |
| UC1 live detection | none (`decide` unchanged, CLI default unchanged) | none: no runtime change |

## 2. Executed checks

Gate ✅ · Must 0 · Should 0 · Nice 0 — 3 checks: Pass 3 · Fail 0 · Mixed 0 · Not tested/N/A 0

| ID | Domain | Check | Covers | Result | Verdict | Evidence | Issues | Shots |
|---|---|---|---|---|---|---|---|---|
| QA-01 | FON | script `--help` and argument errors | UC4 | exits 0 / 2 as specified | PASS | unit tests `test_measure_operating_point.py` | | |
| QA-02 | FON | real sweep, RF-DETR Small on test-v1 | UC4, requirements § Operating point | threshold 0.45, 0 of 780 bees, 2.1 % false alerts | PASS | `scripts/measure_operating_point.py --detector rfdetr …` → `docs/research/operating-point-test-v1.md` | | |
| QA-03 | DAT | "never a bee as target above threshold" | UC4 | 0 bees as target at every grid point ≥ 0.05 | PASS | sweep table, column bees → target | | |

- [x] Every planned check of section 1 appears above.
- [x] Every row has evidence or a not-tested reason.

## 3. Findings to act on

None.

## 4. Not tested

None. No screenshots: command-line script, no UI.

## 5. Delta vs previous pass

First pass.
