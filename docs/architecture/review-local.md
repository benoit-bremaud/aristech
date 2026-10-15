# Local review — aristech (PR #37, Codex P1 class-map fix)

- Date: 2026-10-15
- Commit: 0c3e4d5 (+ review fixes, amended)
- Scope: branch diff origin/feat/m4-measure-script...HEAD
- Checks run: design · docs · tests · security · correctness
- Verdict: ship · Must 0 · Should 4 (3 applied) · Nice 5

## 🔴 Must Have
_None._

## 🟡 Should Have
- `scripts/measure_operating_point.py:39` `[docs]` · `_parse_class_map` docstring missed the new rule and `ValueError` contract · applied.
- `tests/unit/scripts/test_measure_operating_point.py` `[tests|correctness|design]` · exit-2 assertions did not pin the cause; no negative bee case · applied (caplog asserts + no-warning test).
- `scripts/measure_operating_point.py:48` `[correctness]` · duplicate class ids silently overwrite (pre-existing) · deferred to B3 tests/cleanup.
- `scripts/measure_operating_point.py:109` `[design]` · class-map rules split between parser and `main` · deferred (KISS for a script).

## 🔵 Nice to Have
- Untested parser error paths (no `:`, unknown species, non-int id) `[tests]`.
- Wrap `int()` error for a clearer message `[correctness]`.
- `main` docstring with exit codes `[docs]`.
- Mixed French/English log messages, emoji in warning `[design]` (pre-existing style).
- `exec_module` without `sys.modules` registration in tests `[correctness]`.

## ⚪ Disagree / Intentional
- Tests load the script via `importlib` and call a private helper · scripts are not a package; acceptable until the parser moves into `aristech/`.

## Per-dimension summary
- Design: proportionate, no over-engineering · Docs: one stale docstring, fixed · Tests: trustworthy, assertions tightened · Security: nothing found · Correctness: no bugs; duplicate-id overwrite pre-existing.
