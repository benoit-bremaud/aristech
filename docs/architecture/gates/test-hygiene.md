# Conception gate — test-hygiene (brick B3)

| Item | Status | Evidence |
|---|---|---|
| Spec complete, testable acceptance criteria | ✅ | `specs/test-hygiene.md` (AC1–AC8) |
| UML updated | ➖ | No production code changes |
| ADRs accepted | ➖ | No structuring decision; options scored in chat (M1/M2 fix A 455/500, S5 in B3 370/500) |
| Dependency rule kept | ✅ | Tests only; fakes replace `torch`/`cv2` at the boundary, the domain is never mocked |
| Test strategy | ✅ | Unit tests only; integration/e2e deselected by default |
| Risks | ✅ | Default `-m` deselection hides integration tests from a bare `pytest`; mitigated by `make test-integration` |

## Sign-off

- Owner: Benoît Bremaud — ☑ approved (date: 2026-10-16)
