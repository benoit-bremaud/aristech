# QA checklist — logs folder on a fresh checkout (#143)

The CLI must start and write its log file on a fresh checkout that has no `logs/` folder.

| Date | Head SHA | Level | Environment | Branch / PR |
|---|---|---|---|---|
| 2026-11-02 | 656a7a7 + diff | smoke | local, laptop | fix/143-create-logs-folder |

## 1. Coverage

- [x] [`traceability/matrix.md`](../traceability/matrix.md) needs no change: no use case changes,
      only the logging start-up of the CLI.
- [x] Every row below has at least one planned check.

| Use case / requirement | What the diff changes | Planned checks |
|---|---|---|
| CLI start-up (logging setup) | creates the parent folder of every file handler | QA-01, QA-02 |

## 2. Executed checks

Gate ✅ · Must 0 · Should 0 · Nice 0 — 2 checks: Pass 2 · Fail 0 · Mixed 0 · Not tested/N/A 0

| ID | Domain | Check | Covers | Result | Verdict | Evidence | Issues | Shots |
|---|---|---|---|---|---|---|---|---|
| QA-01 | FON | fresh `git clone`, no `logs/`, run `python -m aristech.interface.cli.main` | #143 | rc 0, `logs/app.log` created with the two start-up lines, no fallback warning | PASS | `ls logs` → `app.log` (170 B) | | none: CLI |
| QA-02 | ROB | unit test without the fix | #143 | `test_creates_missing_log_folder` fails without the fix, passes with it | PASS | `pytest -k log` | | none: CLI |
