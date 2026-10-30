# Conception gate — local CI (local CI tiers, #109)

| Item | Status | Evidence |
|---|---|---|
| Spec complete, testable acceptance criteria | ✅ (no spec: tooling-only change, ADR-0027 stands in) | Issue #109 "Done": `just check` green locally and run by the pre-push hook; ADR-0027 § Decision |
| UML updated | ✅ | `diagrams/local-ci/01-activity.md` |
| ADRs accepted | ✅ | ADR-0027 (D1 A 470/500, D2 A 430/500; owner choices 2026-10-30) |
| Dependency rule kept | ✅ | No `src/` change |
| Test strategy | ✅ | `scripts/test-local-ci.sh` (recipes compose, `lefthook validate`, commit-msg check, staged secret refused), run by `just check` |
| Risks | ✅ | Hooks shared by every worktree (mitigated: no-op without `lefthook.yml`); Semgrep offline (mitigated: visible warning, not green in review) |

## Sign-off

- Owner: Benoît Bremaud — ☑ approved (date: 2026-10-30)
