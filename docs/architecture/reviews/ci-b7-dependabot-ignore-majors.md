# Pre-push review — ci/b7-dependabot-ignore-majors (brick B7 follow-up)

- Date: 2026-10-16 · Spec: `specs/dependabot-major-holds.md` · Gate: `gates/dependabot-major-holds.md`
  (owner-signed) · Decision: ADR-0012

## Diff

`.github/dependabot.yml` (two `ignore` entries, comment citing ADR-0012), spec, gate, this report,
traceability note.

## Checks

| AC | Check | Result |
|---|---|---|
| AC1 | YAML parses (`yaml.safe_load`); `ignore` / `update-types` semantics confirmed against the current GitHub Dependabot options reference | ✅ |
| AC2 | PR #75 closed with a reason after merge | ⏳ post-merge |
| AC3 | gitleaks (staged); CI | ✅ / ⏳ |

## Findings

- **Must**: none. **Should**: none.
- **Nice**: none. Risk A1 (security PR suppressed for a fix that only exists in the next major) is
  accepted by design: the alert stays visible and triggers a new ADR.
