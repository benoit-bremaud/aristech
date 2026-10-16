# Design dossier

Source of truth for how aristech is designed. `docs/architecture.md` is a one-page as-built
overview that points here.

| Folder | Content |
|--------|---------|
| [`specs/`](specs/README.md) | Feature specifications (need, actors, acceptance criteria) |
| [`diagrams/`](diagrams/README.md) | UML diagrams in Mermaid, one folder per feature |
| [`traceability/`](traceability/README.md) | Requirement → design → code → test matrix |
| [`gates/`](gates/README.md) | Conception gate (PDR) checklists, one per feature |
| [`reviews/`](reviews/README.md) | Audits and pre-push review reports |
| [`../decisions/`](../decisions/README.md) | Architecture Decision Records |

## Flow for a feature

1. Spec in `specs/<feature>.md`.
2. UML in `diagrams/<feature>/` (use-case, sequence, component, class, state, data-flow as
   relevant).
3. ADR for every structuring choice.
4. Conception gate passed in `gates/<feature>.md` (owner sign-off).
5. Code + tests; traceability row updated.
6. Pre-push review report in `reviews/<branch>.md`.
