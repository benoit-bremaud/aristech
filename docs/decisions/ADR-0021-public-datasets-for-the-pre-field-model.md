# ADR-0021: Public datasets for the pre-field model

- Status: Proposed
- Date: 2026-10-19 (issue #95, spec annotation-pipeline A7)

## Context

Licence facts (checked 2026-10-19): Roboflow *hornet-behavior* v1 — CC BY 4.0, 364 images,
crabro/velutina, no bee (owner download, M3 report). Sledevic *bee detection on landing boards*
(Mendeley 10.17632/8gb9r2yhfc.6) — **CC BY 4.0 verified**, ~7,200 YOLO-labelled 1920×1080 frames
of hive entrances, bee only. iNaturalist research-grade photos — licence per photo (CC BY / CC0
selectable), species labels only, no boxes. Other Roboflow sets (NUCH-B, vespa-48ocu, hornet-t4fss)
show CC BY / public domain in search snippets but were **not verified** (pages need login). VespAI's
dataset is CC BY-NC-SA: excluded. Bee sets on IEEE DataPort / VnPollenBee: research-only or unknown.

## Options (MCDA)

Script: [`mcda/adr_0018_0022_annotation_pipeline.py`](mcda/adr_0018_0022_annotation_pipeline.py). Scores 0–5, weights /100, totals /500; scores are estimates unless marked verified.

| Option | Licence certainty 35 | Class coverage 25 | Entrance context 20 | Effort 20 | Total |
|---|---|---|---|---|---|
| A. Roboflow hornet-behavior + Sledevic bees + iNaturalist CC BY/CC0 (velutina, crabro, other insects; boxed with pre-annotation) | 5 | 5 | 3 | 2 | **400** |
| B. Roboflow hornet-behavior + Sledevic bees only | 5 | 3 | 3 | 4 | 390 |
| C. A + unverified Roboflow sets once their licence is checked | 3 | 5 | 3 | 3 | 350 |

Sensitivity: class coverage 35 → A 425; effort 30 → B 400, A 370 (B leads). **Fragile A/B on
effort**: staircase — B first (first model), then iNaturalist as the next increment of the same
brick. C's sets enter later only through the licence register once verified (spec A2).

## Decision

- Step 1: import Roboflow hornet-behavior v1 and a capped sample of Sledevic frames (bee class).
- Step 2: add iNaturalist CC BY / CC0 research-grade photos for velutina, crabro and "other"
  insects (wasps, flies), boxed in X-AnyLabeling with model pre-annotation.
- `test-v1` is frozen after step 2 so it covers all four classes; a model trained after step 1 is
  reported on the validation split only.
- Attribution text for every source is kept in the licence register (CC BY requires it).

## Consequences

- Hive-entrance context comes mostly from the bee set; hornets are mostly close-ups → field data
  (C1) remains necessary (M5).
