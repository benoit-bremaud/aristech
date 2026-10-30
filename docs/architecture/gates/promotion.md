# Conception gate — promotion (branching and promotion model, #112)

| Item | Status | Evidence |
|---|---|---|
| Spec complete, testable acceptance criteria | ✅ (no spec: process-only change, ADR-0025 stands in) | ADR-0025 § Decision (the table and the rules that follow it are the acceptance criteria) |
| UML updated | ✅ | `diagrams/promotion/01-activity.md` |
| ADRs accepted | ✅ | ADR-0025 (C 430/500 vs B 440, owner-weighted choice 2026-10-30) |
| Dependency rule kept | ✅ | No `src/` change |
| Test strategy | ✅ | Process-only change; verified by the rulesets after merge and by #109's `just check` |
| Risks | ✅ | Drift between `dev` and `main` (mitigated: back-merge rule); squash into `main` by mistake (mitigated: ruleset allows merge commit only) |

## Sign-off

- Owner: Benoît Bremaud — ☑ approved (date: 2026-10-30)
