# ADR-0008: Adopt the V-SEA / cubbies working method

- Status: Accepted
- Date: 2026-10-15 (audit), started 2026-10-16 (PR #49)

> Retroactive ADR (written 2026-10-16, brick B1). The decision predates the ADR practice;
> the MCDA scores are reconstructed from the rationale recorded at the time and were not
> owner-weighted then. Source of truth for the original wording: the cited PRs and `PROJECT_LOG.md`.

## Context

The 2026-10-15 audit found no design dossier, ADRs, UML or conception gate (finding M7) on a
project the owner considers large and complex.

## Options (MCDA)

Criteria and weights (C1…): traceability 35, design quality 30, overhead 20, consistency with other projects 15. Scores 0–5.

| Option | C1 | C2 | C3 | C4 | Total /500 |
|---|---|---|---|---|---|
| A. Full method: dossier, ADRs, UML-first, PDR gate, pre-push reports, one chat per brick | 5 | 5 | 2 | 5 | 440 |
| B. Lightweight: ROADMAP + PROJECT_LOG only | 2 | 2 | 5 | 1 | 245 |
| C. ADRs only | 4 | 3 | 4 | 3 | 355 |

## Decision

Option A, rolled out in bricks B1 to B6 (see `docs/architecture/reviews/audit-2026-10-15.md`).

## Consequences

- Every feature now passes spec → UML → ADR → gate before code.
- Project rules live in `CLAUDE.md`.
