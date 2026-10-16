# ADR-0001: Clean Architecture with ports and optional heavy extras

- Status: Accepted
- Date: 2026-05-19 (PR #1), extended 2026-05-21 (PR #22)

> Retroactive ADR (written 2026-10-16, brick B1). The decision predates the ADR practice;
> the MCDA scores are reconstructed from the rationale recorded at the time and were not
> owner-weighted then. Source of truth for the original wording: the cited PRs and `PROJECT_LOG.md`.

## Context

The legacy code was a flat script layout mixing Keras training, camera access and logic. The
project needs to swap detectors (VespAI now, a fine-tuned or permissively licensed model later),
run the core on a Raspberry Pi, and unit-test decisions without torch or a camera.

## Options (MCDA)

Criteria and weights (C1…): testability 30, swappable infrastructure 30, simplicity 20, install weight 20. Scores 0–5.

| Option | C1 | C2 | C3 | C4 | Total /500 |
|---|---|---|---|---|---|
| A. Clean Architecture src-layout, ports at the boundaries, heavy libs in optional extras | 5 | 5 | 3 | 5 | 460 |
| B. Flat package, direct imports of torch/cv2 | 2 | 1 | 5 | 1 | 210 |
| C. Plugin framework (entry points, dynamic loading) | 4 | 5 | 1 | 4 | 370 |

## Decision

Option A. `domain/` → `application/` (use cases + ports) → `infrastructure/` adapters, wired in
the `interface/cli` composition root. Heavy dependencies live in extras (`vision`, `audio`,
`training`, `connectivity`); the core install only needs PyYAML and python-dotenv.

## Consequences

- Use cases are unit-tested with hand-written fakes at the ports, no torch in CI.
- A port needs a present force; the audit (S1) found five speculative ports to remove (B5).
- `evaluation/` reuses the `HornetDetector` port as a second consumer.
