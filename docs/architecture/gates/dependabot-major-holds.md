# Conception gate — dependabot-major-holds (brick B7 follow-up)

| Item | Status | Evidence |
|---|---|---|
| Spec complete, testable acceptance criteria | ✅ | `specs/dependabot-major-holds.md` (AC1–AC3) |
| UML updated | ✅ | Not needed: repository configuration only |
| ADRs accepted | ✅ | ADR-0012 (accepted); this applies its consequence, no new ADR |
| Dependency rule kept | ✅ | No code change |
| Test strategy | ✅ | YAML parse; CI green; next weekly Dependabot run omits the two majors |
| Risks | ✅ | A1: a security fix only in the next major gets no Dependabot PR (alert still visible) |

## Sign-off

- Owner: Benoît Bremaud — ☑ approved (date: 2026-10-16; option "close #75 + ignore majors",
  chosen in chat)
