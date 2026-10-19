# Spec — annotation pipeline and first pre-field model

> **Status**: Accepted (gate signed 2026-10-19) · **Brick**: annotation pipeline (winter 2026–27, issue #95) ·
> **Roadmap gate**: frozen test set defined, licences recorded ·
> **Related**: ADR-0015 (own model, permissive base), ADR-0014 (two operating points),
> ADR-0003 (legal floor), ADR-0018 to ADR-0022 (this brick), specs
> [own-vision-model](own-vision-model.md), [capture-rig](capture-rig.md),
> [m3-report](m3-report.md) · **Use cases**: UC8, UC9, UC3

## Need

The owner wants **our own hornet photo database** (owner, 2026-10-19), labelled with four classes —
*V. velutina* (target), *V. crabro*, *Apis mellifera*, other — that:

1. records, for **every** image, where it comes from and under which licence, so that only
   commercially compatible data (CC BY, CC BY-SA, CC0, or own captures) ever trains a product model;
2. holds a **frozen test set** that never changes once frozen, never leaks into training and is
   the yardstick every model (VespAI baseline, own models) is scored on;
3. ingests public data now and **C1 captures later** with the same steps;
4. lets a first own model be trained on public data only ("pre-field", spec own-vision-model A1)
   and scored against the VespAI baseline (M3 report) before the 2027 season.

Today the only data is a git-ignored Roboflow export and an old, licence-less `data/raw_images/`
scrape; nothing records licences, and the existing `datasets/distribute.py` split is a random file
move that would leak near-duplicate frames across splits.

## Actors

- **Researcher** (primary; the owner) — adds sources, annotates, freezes the test set, trains,
  reads reports.
- **Public dataset publisher** (secondary, external) — provides images and their licence.
- **Capture rig C1** (secondary, system) — provides segments with sidecar metadata
  (`SegmentMetadata`: rig, hive, site, start time).

## Use cases (actor goals)

- **UC8 Annotate images for the database** — UC8a register a source and its licence; UC8b import
  and annotate (pre-annotation by a model, corrected by hand); UC8c freeze the test set.
- **UC9 Train and compare an own detector** — fine-tune the chosen base on the training split,
  score it with UC3 on the frozen set against VespAI.

## Main scenario (public data, pre-field)

1. The researcher registers a source in the **licence register** (name, URL, version, licence,
   attribution text, download date). A source with a non-compatible or unclear licence is refused.
2. The researcher downloads the export into `data/external/<source>/` (git-ignored) and runs the
   **import** command: it hashes every image (SHA-256), maps the source's classes to the four
   database classes, assigns each image a **group key** (the unit that must never be split across
   train / test) and writes one row per image to the dataset **manifest** (committed, no pixels).
3. The researcher annotates or corrects labels in the annotation tool and exports them in the
   canonical label format; the import refreshes the manifest's label hash.
4. The researcher runs the **split** command: groups are assigned to train / validation / test
   deterministically from the manifest (seeded, by group, stratified on class presence).
5. The researcher runs the **freeze** command: the test rows (image hashes + label hashes) are
   written to a frozen test-set file with an id (`test-v1`) and its own hash, committed.
   From then on, any later split that would move a frozen image out of test, or put an image
   whose group is in the frozen set into train, fails.
6. The researcher trains the first model on the training split (UC9) and runs the harness (UC3)
   on the frozen set; the report records the dataset manifest hash, the frozen-set id, the base
   model and its licence, and per-class P/R next to VespAI's.

## Alternative scenarios

- **A1 C1 captures (2027).** Frames sampled from C1 clips are imported with group key
  `<hive_id>/<UTC date>` taken from the sidecar, licence `own`. They append to the database; the
  frozen set gets a **new version** (`test-v2`) that adds field groups; `test-v1` stays readable so
  older results stay comparable.
- **A2 Licence unclear or NC.** Import refuses the source (exit 2, message); nothing is written.
- **A3 Duplicate image** (same SHA-256 in two sources, or re-import). One manifest row; the image
  keeps the group it was first given; a duplicate across groups **merges** those groups, so a frozen test image can never reappear in train.
- **A4 Unknown source class.** Import fails with the list of unmapped classes; the researcher
  extends the class map explicitly (no silent `other`).
- **A5 Frozen-set violation.** Split exits 2 naming the offending images; the frozen file is never
  rewritten in place.
- **A6 Captive-lab footage** (spec own-vision-model A4) is tagged `captive` and is never eligible
  for any test set.
- **A7 Not enough bee or "other" images in public CC BY data.** The gap is recorded in the
  dataset report; the first model is still trained, with its class coverage stated.

## Acceptance criteria

- **AC1** Every manifest row has a source id present in the licence register; the register has a
  licence for every source; an import from a source whose licence is not in the allow-list
  (`CC-BY-4.0`, `CC-BY-SA-4.0`, `CC0-1.0`, `own`) fails with exit code 2.
- **AC2** The manifest and the licence register are plain text, committed, and contain no pixels;
  images stay git-ignored under `data/`.
- **AC3** Labels use the canonical format of ADR-0018 with the four classes in a fixed order;
  source class maps are explicit and an unmapped class fails the import.
- **AC4** The split is deterministic (same manifest + seed → same assignment) and **no group key
  appears in two splits** (unit-tested).
- **AC5** The frozen test set file lists image and label hashes and carries its own hash; split and
  train commands refuse to run if a frozen image is missing from test or a frozen group appears in
  train (unit-tested).
- **AC6** C1 sidecar metadata maps to a manifest row (group key `<hive_id>/<date>`, licence `own`)
  through the same import path (unit-tested with a fake sidecar).
- **AC7** The first model's weights licence and code licence are permissive (ADR-0022) and recorded
  in its report; no training dependency enters the core `dependencies`.
- **AC8** One command reproduces the first-model report on the frozen set, with VespAI's numbers on
  the same set beside it; dataset manifest hash, frozen-set id and model hash are recorded.
- **AC9** Domain/application code keeps the dependency rule; the pipeline core is stdlib only and
  runs in CI without images.

## Out of scope

- The M5 gate (own model beats VespAI on **field** data) — needs the 2027 season.
- Hosting the images anywhere public; redistributing third-party images.
- The C1 frame-sampling script itself (written when C1 footage exists; this brick fixes its
  contract, AC6).
