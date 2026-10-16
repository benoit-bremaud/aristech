# Conception gate — repo-hygiene (brick B6a)

| Item | Status | Evidence |
|---|---|---|
| Spec complete, testable acceptance criteria | ✅ | `specs/repo-hygiene.md` (AC1–AC8) |
| UML updated | ✅ | Not needed: no code structure change |
| ADRs accepted | ✅ | ADR-0011 (Sphinx stub A 475/500; lint parity A 500/500, owner-chosen 2026-10-16) |
| Dependency rule kept | ✅ | No `src/` change |
| Test strategy | ✅ | Tooling-only change; `make lint type-check test-unit` and `pre-commit run -a` |
| Risks | ✅ | `pip install aristech[docs]` breaks; newer ruff may flag new rules (fixed in the same PR) |

## Sign-off

- Owner: Benoît Bremaud — ☑ approved (date: 2026-10-16)
