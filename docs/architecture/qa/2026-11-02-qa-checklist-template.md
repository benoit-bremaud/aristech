# QA checklist — QA checklist template (2026-11-02)

First use of [`checklist-template.md`](checklist-template.md), on the branch that adds it.

| Date | Head SHA | Level | Environment | Branch / PR |
|---|---|---|---|---|
| 2026-11-02 | f9c4bb2 + this branch's diff | smoke | local, laptop | `chore/134-qa-checklist-template` |

## 1. Coverage

The diff touches process documents only: no use case of
[`traceability/matrix.md`](../traceability/matrix.md) and no section of
[`requirements.md`](../../requirements.md) changes.

- [x] [`traceability/matrix.md`](../traceability/matrix.md) is up to date with the diff (no
      code or test change, no row to update).
- [x] Every row below has at least one planned check, or a reason why none applies.

| Use case / requirement | What the diff changes | Planned checks |
|---|---|---|
| None (process: pre-merge gate step 5) | QA checklist template, gate hooks in CONTRIBUTING, PR template, dossier READMEs | QA-01, QA-02, QA-03 |

## 2. Executed checks

Gate ✅ · Must 0 · Should 0 · Nice 0 — 3 checks: Pass 3 · Fail 0 · Mixed 0 · Not tested/N/A 0

| ID | Domain | Check | Covers | Result | Verdict | Evidence | Issues | Shots |
|---|---|---|---|---|---|---|---|---|
| QA-01 | DOC | Markdown lint of the changed files | gate step 5 | Pass | PASS | `npx markdownlint-cli2@0.18.1 <6 files>` → `Summary: 0 error(s)` | | |
| QA-02 | DOC | Relative links of the new and changed READMEs resolve | gate step 5 | Pass | PASS | shell loop over `](…)` targets → no broken link | | |
| QA-03 | FON | Local CI still green | gate step 5 | Pass | PASS | `mise x -- just check` → exit 0, 268 passed, coverage 96.46 %, gitleaks no leaks | | |

- [x] Every planned check of section 1 appears above.
- [x] Every row has evidence or a not-tested reason.

## 3. Findings to act on

None.

## 4. Not tested

None. No runtime change, so no product run.

## 5. Delta vs previous pass

First pass with this checklist.
