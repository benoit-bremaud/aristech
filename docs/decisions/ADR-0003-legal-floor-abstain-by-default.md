# ADR-0003: Legal floor: never act on a bee, abstain by default

- Status: Accepted
- Date: 2026-05-19 (PR #4)

> Retroactive ADR (written 2026-10-16, brick B1). The decision predates the ADR practice;
> the MCDA scores are reconstructed from the rationale recorded at the time and were not
> owner-weighted then. Source of truth for the original wording: the cited PRs and `PROJECT_LOG.md`.

## Context

Harming a protected pollinator is a criminal offence in France (Code de l'environnement,
art. L411-1 and L415-3). Any action taken on a misclassified honeybee is therefore not a
quality defect but a legal one.

## Options (MCDA)

Criteria and weights (C1…): legal safety 50, hornet coverage 25, simplicity 25. Scores 0–5.

| Option | C1 | C2 | C3 | Total /500 |
|---|---|---|---|---|
| A. Abstain (do not act) on low confidence + geometric no-spray zone independent of the classifier | 5 | 3 | 3 | 400 |
| B. Act on the most likely class | 1 | 5 | 5 | 300 |
| C. Human confirmation for every action | 5 | 1 | 2 | 325 |

## Decision

Option A. The decision layer defaults to *abstain → do not act* below the operating threshold,
and a no-spray exclusion zone around the landing board is enforced independently of the classifier
(to be modelled with the deterrence module).

## Consequences

- Drives the operating-point policy (ADR-0004).
- The abstention must be reachable in the live path; the audit (M3) found it is not yet (B4).
