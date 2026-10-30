# Pre-push review — ci/105-lint-scripts

Review of the `scripts/` lint extension and the S7517 fix (issues #105, #50) before the push.

- Date: 2026-10-30
- Scope: branch diff `origin/dev...HEAD`
- Verdict: ship as-is · Must 0 · Should 0 · Nice 0

## Pre-merge gate

| Step | Result |
|---|---|
| 1 Tests | ✅ 270 unit on 3.11 and 3.12 |
| 2 Coverage | tests 97.7 % (floor 80) |
| 3 SonarQube | ✅ PASSED; python:S7517 open issues 2 → 0 |
| 4 Secrets | ✅ gitleaks clean · diff read: nothing sensitive |
| 5 QA pass | ✅ smoke: tooling and one behaviour-preserving line |

## Content

- `scripts/prepare_directories.py` and `scripts/prepare_images.py` removed: preprocessing for the
  legacy Keras training (150 × 150 resize, single-class folders) removed by ADR-0010; nothing
  references them.
- ruff check and format now cover `scripts/` (`just lint`, the pre-commit glob, `make lint` and
  `make format`); `measure_operating_point.py` reformatted.
- `EvaluationReport.all_class_metrics`: the label set is built from the key pairs in one pass
  (python:S7517), same result; covered by the existing metrics tests.
- osv-scanner runs with `--no-resolve`: the lock is complete, and the transitive resolution
  (deps.dev) failed twice in a row on this branch.

## 🔴 Must Have

_None._

## 🟡 Should Have

_None._

## 🔵 Nice to Have

_None._

## ⚪ Disagree / Intentional

_None._
