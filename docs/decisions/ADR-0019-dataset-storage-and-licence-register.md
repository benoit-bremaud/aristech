# ADR-0019: Committed manifest and licence register; pixels stay git-ignored

- Status: Proposed
- Date: 2026-10-19 (issue #95, spec annotation-pipeline AC1, AC2)

## Context

The repository is public until the first production deployment; third-party images may not be
redistributed by us beyond their licence terms, and own captures may show the apiary. The gate asks
that licences be recorded. C1 will add tens of thousands of frames in 2027.

## Options (MCDA)

Script: [`mcda/adr_0018_0022_annotation_pipeline.py`](mcda/adr_0018_0022_annotation_pipeline.py). Scores 0–5, weights /100, totals /500; scores are estimates unless marked verified.

| Option | Licence compliance 30 | Reproducibility 25 | Simplicity 25 | Scale to C1 20 | Total |
|---|---|---|---|---|---|
| A. Committed CSV `licences.csv` + `manifest.csv` (hashes, no pixels); images git-ignored under `data/`, re-downloadable, owner backup | 5 | 4 | 5 | 3 | **435** |
| B. DVC with a private remote | 4 | 5 | 2 | 5 | 395 |
| C. Git LFS in the repository | 0 | 5 | 3 | 2 | 240 |

Sensitivity: scale-to-C1 40 → B 435, A 395 (B leads); reproducibility 40 → A 430, B 425.
**B wins only if field-data scale dominates**: revisit at the 2027 capture season (A1 of the spec),
DVC can be added on top of A without changing the manifest.

## Decision

- `licences.csv` (one row per source: id, name, URL, version, SPDX licence,
  attribution, retrieval date, captive flag) and `manifest.csv` (one row per image:
  SHA-256, source id, source path, group key, label SHA-256, classes, split) live in the repository
  under `data/registry/` (whitelisted in `.gitignore`).
- Allow-list: `CC-BY-4.0`, `CC-BY-SA-4.0`, `CC0-1.0`, `own`. Anything else is refused at import.
- Pixels stay under `data/external/<source>/` (third party) and `data/own/` (C1), git-ignored.

## Consequences

- Anyone can verify the licence of every training image from the repository alone.
- A lost local copy is rebuilt from the sources (hash-checked); own captures need the owner's backup.
