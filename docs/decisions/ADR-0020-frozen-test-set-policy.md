# ADR-0020: Frozen test set — group-keyed, hash-listed, versioned and append-only

- Status: Accepted (owner, 2026-10-19)
- Date: 2026-10-19 (issue #95, spec annotation-pipeline AC4, AC5; roadmap gate)

## Context

The roadmap gate requires a frozen test set. Random image splits leak: Roboflow exports contain
augmented copies of one photo (file stem `<orig>_jpg.rf.<hash>`), and C1 frames of one visit are
near-duplicates. ADR-0015 already requires a split by day and hive.

## Options (MCDA)

Script: [`mcda/adr_0018_0022_annotation_pipeline.py`](mcda/adr_0018_0022_annotation_pipeline.py). Scores 0–5, weights /100, totals /500; scores are estimates unless marked verified.

| Option | No leakage 35 | Stability 25 | Field relevance 20 | Simplicity 20 | Total |
|---|---|---|---|---|---|
| A. Split by **group key**, test rows frozen as a hash list in `test-vN.csv` with its own digest; new versions only add | 5 | 5 | 4 | 4 | **460** |
| B. Random image hold-out | 1 | 3 | 2 | 5 | 250 |
| C. Whole source held out (e.g. one public set = test) | 5 | 4 | 2 | 4 | 395 |

Sensitivity: simplicity 30 → A 450; field relevance 40 → A 450. **Robust.**

## Decision

- Group key: public sets → the original photo stem (Roboflow: text before `_jpg.rf.`; others:
  the source's own scene/video id when given, else the file stem) — a weaker proxy for ADR-0015's day-and-hive rule, which public data cannot carry; C1 → `<hive_id>/<UTC date>`.
- Split: deterministic, by group, seeded, ~70/15/15, stratified on class presence.
- `data/registry/test-v1.csv` freezes image + label hashes and is never edited; a label fix in a
  frozen image produces `test-v2`, never an in-place change. Split and training refuse to run if a
  frozen image leaves test or a frozen group enters train.
- Captive-lab images are never eligible for test (spec own-vision-model A4).
- `test-v1` is **pre-field**: public data only; field groups enter in `test-v2` (2027).

## Consequences

- Results are always quoted with their test-set id.
- The M5 gate (beat VespAI on field data) is measured on `test-v2` or later.
