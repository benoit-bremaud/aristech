# Conception gate — yagni-training-removal (brick B5)

| Item | Status | Evidence |
|---|---|---|
| Spec complete, testable acceptance criteria | ✅ | `specs/yagni-training-removal.md` (AC1–AC7) |
| UML updated | ✅ | `diagrams/detection/03-component.md`, `04-class.md` notes |
| ADRs accepted | ✅ | ADR-0010 (distribute A 370/500, extras A 470/500, owner-chosen 2026-10-16) |
| Dependency rule kept | ✅ | Deletions only; `datasets/` imports stdlib only |
| Test strategy | ✅ | `distribute` unit tests move with the code; false-confidence tests die with `training/` |
| Risks | ✅ | Someone relying on `pip install aristech[training]` breaks; legacy code stays in git history |

## Sign-off

- Owner: Benoît Bremaud — ☑ approved (date: 2026-10-16)
