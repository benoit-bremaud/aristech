# QA checklist — template

Copy this file to `docs/architecture/qa/<YYYY-MM-DD>-<topic>.md` at every QA pass, fill every
section, and link the copy from step 5 of the branch's review report. Delete this paragraph and
the hints in angle brackets.

| Date | Head SHA | Level | Environment | Branch / PR |
|---|---|---|---|---|
| <YYYY-MM-DD> | <sha> | <smoke / pass / full> | <local / staging, laptop / Pi> | <branch>, #<PR> |

## 1. Coverage

The QA matrix must cover what the diff touches. One row per use case of
[`traceability/matrix.md`](../traceability/matrix.md) or section of
[`requirements.md`](../../requirements.md) the diff touches; every other use case is out of scope
for this pass.

- [ ] [`traceability/matrix.md`](../traceability/matrix.md) is up to date with the diff (code and
      test columns of the touched use cases).
- [ ] Every row below has at least one planned check, or a reason why none applies.

| Use case / requirement | What the diff changes | Planned checks |
|---|---|---|
| <UC7 Record synchronised field footage> | <segment timing> | <FON-01, DAT-02> |
| <requirements § Non-functional needs> | <…> | <none: reason> |

## 2. Executed checks

Every planned check gets one row, with evidence: a screenshot file name, a command and its
output, or a file path. A check that could not run is `NOT TESTED` or `BLOCKED`, never `PASS`.
IDs and domains follow the `qa-browser-check` checklist; project-specific checks may use a free
ID (`QA-01`).

Gate <✅ / ❌> · Must <n> · Should <n> · Nice <n> — <n> checks: Pass <n> · Fail <n> · Mixed <n> ·
Not tested/N/A <n>

| ID | Domain | Check | Covers | Result | Verdict | Evidence | Issues | Shots |
|---|---|---|---|---|---|---|---|---|
| <FON-01> | <FON> | <nominal run> | <UC7> | <Pass> | <PASS> | <command → output> | | <01-run.png> |

- [ ] Every planned check of section 1 appears above.
- [ ] Every row has evidence or a not-tested reason.

## 3. Findings to act on

<Ranked Must / Should / Nice, with the issue number, or "None".>

## 4. Not tested

<Check ID — verdict (reason): what would unblock it, or "None".>

## 5. Delta vs previous pass

<Previous checklist path: fixed n, still failing n, new n — or "First pass".>
