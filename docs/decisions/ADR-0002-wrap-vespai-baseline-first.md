# ADR-0002: Wrap the VespAI YOLOv5 model as the first detector

- Status: Accepted
- Date: 2026-05-21 (PR #11), confirmed 2026-05-21 (PR #20)

> Retroactive ADR (written 2026-10-16, brick B1). The decision predates the ADR practice;
> the MCDA scores are reconstructed from the rationale recorded at the time and were not
> owner-weighted then. Source of truth for the original wording: the cited PRs and `PROJECT_LOG.md`.

## Context

Training a hornet detector from scratch needs an annotated corpus the project does not have yet.
VespAI (YOLOv5s detector + ResNet classifier) is published, detects *V. velutina* and *V. crabro*, ships weights and runs on a
Pi 4, but its weights are CC BY-NC-SA and it has no bee class.

## Options (MCDA)

Criteria and weights (C1…): time to a working pipeline 35, detection quality 30, licence freedom 20, effort 15. Scores 0–5.

| Option | C1 | C2 | C3 | C4 | Total /500 |
|---|---|---|---|---|---|
| A. Wrap VespAI behind `HornetDetector`, fine-tune on own data later (M5) | 5 | 4 | 2 | 5 | 410 |
| B. Train an own model first | 1 | 2 | 5 | 1 | 210 |
| C. Generic COCO detector + heuristics | 4 | 1 | 5 | 4 | 330 |

## Decision

Option A. VespAI is loaded from an operator-supplied weights path (never committed), its YOLOv5 detector is wrapped
at runtime in `infrastructure/vision/vespai_detector.py`; the bee is handled as a negative.

## Consequences

- Non-commercial use only; a permissively licensed model is required before any product.
- The M3 measurement on a Roboflow set showed a low hornet recall, which makes the M5 own-data
  fine-tune a real need rather than an optimisation.
