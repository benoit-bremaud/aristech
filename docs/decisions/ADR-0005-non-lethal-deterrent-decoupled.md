# ADR-0005: Non-lethal water-jet deterrent, decoupled from detection and gated by D0

- Status: Accepted
- Date: 2026-05-19 (PR #4), refined 2026-05-22 (PR #30) and 2026-05-23 (PR #34)

> Retroactive ADR (written 2026-10-16, brick B1). The decision predates the ADR practice;
> the MCDA scores are reconstructed from the rationale recorded at the time and were not
> owner-weighted then. Source of truth for the original wording: the cited PRs and `PROJECT_LOG.md`.

## Context

After detection, the system may act. The options range from lethal to alert-only; the efficacy
of any deterrent on *V. velutina* is unproven, and the medium must leave no trace.

## Options (MCDA)

Criteria and weights (C1…): legal and non-target safety 40, colony protection 30, eco-cleanliness 20, cost 10. Scores 0–5.

| Option | C1 | C2 | C3 | C4 | Total /500 |
|---|---|---|---|---|---|
| A. Non-lethal jet, medium open (default pure water), field test D0 before any actuator work | 5 | 4 | 5 | 4 | 460 |
| B. Coil gun (lethal) | 0 | 5 | 3 | 2 | 230 |
| C. Alert only | 5 | 1 | 5 | 5 | 380 |

## Decision

Option A. Deterrence is a separate module that depends only on the detection output and the ports
(Dependency Inversion); detection ships alone as the v1 monitoring deliverable. Solid projectiles
are excluded by the legal floor, leave-no-trace and non-lethal guards.

## Consequences

- No actuator or aiming engineering before a positive D0.
- Multi-modal fusion and the fail-safe default (dry-run vs live) stay open.
