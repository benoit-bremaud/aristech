# ADR-0004: Operating point: lowest threshold with zero bees as target

- Status: Accepted
- Date: 2026-05-21 (PR #11), implemented 2026-05-24 (PR #36)

> Retroactive ADR (written 2026-10-16, brick B1). The decision predates the ADR practice;
> the MCDA scores are reconstructed from the rationale recorded at the time and were not
> owner-weighted then. Source of truth for the original wording: the cited PRs and `PROJECT_LOG.md`.

## Context

The detector outputs a confidence per box. A single threshold decides ACT vs ABSTAIN. ADR-0003
requires zero bees acted upon; hornet recall should be as high as that allows.

## Options (MCDA)

Criteria and weights (C1…): legal floor 45, hornet recall 30, explainability 25. Scores 0–5.

| Option | C1 | C2 | C3 | Total /500 |
|---|---|---|---|---|
| A. Lowest threshold at which zero bees are classified as target, raise if none | 5 | 4 | 5 | 470 |
| B. Threshold maximising F1 | 1 | 5 | 4 | 295 |
| C. Fixed high threshold (e.g. 0.9) | 3 | 2 | 5 | 320 |

## Decision

Option A, in `evaluation/operating_point.py` (`select_operating_point`). `application/decision.py`
exposes `Decision` (ACT / ABSTAIN / IGNORE) and a pure `decide()`; a target below the threshold
abstains explicitly. This refines the "high confidence threshold + abstention" wording of
`docs/requirements.md`: the threshold is measured, not fixed high.

## Consequences

- The threshold is measured on an annotated set (`scripts/measure_operating_point.py`, PR #37, issue #18).
- Known gap: the CLI pre-filters detections at the same confidence, so ABSTAIN never fires live
  (`interface/cli/main.py`, audit M3); fixed in brick B4.
