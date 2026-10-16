# ADR-0007: Security CI baseline and local SonarQube

- Status: Accepted
- Date: 2026-10-16 (PR #39, PR #51)

> Retroactive ADR (written 2026-10-16, brick B1). The decision predates the ADR practice;
> the MCDA scores are reconstructed from the rationale recorded at the time and were not
> owner-weighted then. Source of truth for the original wording: the cited PRs and `PROJECT_LOG.md`.

## Context

The repository went public on 2026-10-15 without secret detection, SAST or dependency checks.
Code quality and coverage were only visible through ad-hoc runs.

## Options (MCDA)

Criteria and weights (C1…): risk reduction 40, cost 25, maintenance 20, signal quality 15. Scores 0–5.

| Option | C1 | C2 | C3 | C4 | Total /500 |
|---|---|---|---|---|---|
| A. Gitleaks, CodeQL, dependency review, Scorecard, Dependabot in CI + local SonarQube scan on main | 5 | 5 | 4 | 4 | 465 |
| B. Gitleaks only | 2 | 5 | 5 | 3 | 350 |
| C. Hosted SonarCloud with PR decoration | 4 | 3 | 4 | 5 | 390 |

## Decision

Option A. One workflow per tool, actions pinned by SHA; `make sonar` scans `main` on the shared
local Community Build (no PR decoration). The local review report remains the PR gate.

## Consequences

- Weekly grouped Dependabot PRs need regular triage.
- SonarQube does not judge PR branches.
