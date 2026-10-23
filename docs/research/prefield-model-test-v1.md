# Pre-field model (RF-DETR Small) vs VespAI on test-v1

> **Issue**: #95, PR 4 · **Date**: 2026-10-23 · **Spec**: annotation-pipeline AC7, AC8 ·
> **ADRs**: ADR-0022, ADR-0024 · **Tables (generated)**: [prefield-model-test-v1-tables.md](prefield-model-test-v1-tables.md)

## What was run

- **Data**: manifest sha256 `35c77b53…45d8b8`, trained on train (1,560 images); validation (251) picks the checkpoint and stops early.
  Scored on **test-v1** (288 images, 1,032 boxes, sha256 `6d4f5dc5…54d9`). The test labels
  come from the committed snapshot. The owner checked a 30-image contact sheet of iNaturalist
  boxes before training and accepted all of them
  ([list](../architecture/qa/2026-10-23-box-spot-check.csv)).
- **Model**: RF-DETR Small at 512 px, fine-tuned from its COCO checkpoint with `rfdetr` 1.11.2.
  Code and base weights are Apache-2.0. Training ran 32 epochs on an RTX 4070 Laptop (about
  50 min, effective batch 16). Early stopping kept epoch 21 (validation mAP 0.557).
  Weights sha256 `3df5a250…92fcab`; they stay git-ignored.
- **Baseline**: VespAI `yolov5s-all-data.pt` (sha256 `1fff0bde…3694`, CC BY-NC-SA,
  comparison only). It runs on the same images through the same UC3 harness.
- **Reproduce**: `make prefield-train STORE=…`, then `make prefield-report VESPAI_WEIGHTS=…
  YOLOV5_DIR=…`. Environment: [prefield-model-requirements.txt](prefield-model-requirements.txt).

## Results at conf ≥ 0.5 (IoU ≥ 0.5)

| Class | RF-DETR P | RF-DETR R | VespAI P | VespAI R |
|---|---:|---:|---:|---:|
| **vespa_velutina** (202 boxes) | **0.571** | **0.480** | 0.000 | 0.000 |
| vespa_crabro (32) | 0.885 | 0.719 | 0.016 | 0.031 |
| apis_mellifera (780) | 0.964 | 0.860 | — (no class) | — |
| other (18) | 0.545 | 0.667 | — (no class) | — |

At conf ≥ 0.8 velutina recall falls to 0.010, while crabro (0.917 / 0.688) and bees
(0.998 / 0.674) hold. The model is not confident on velutina yet, so 0.8 is not a usable
operating point for the target class.

## Reading

The per-source and confusion counts below come from the local run (one-off breakdown of the
same samples); they are not in the generated tables.

- **The own model beats VespAI on every class of test-v1.** On this set VespAI finds no
  velutina at all (0/202), in line with the M3 finding that it does not transfer.
- **Zero bees are called hornets**: no bee box was predicted as velutina or crabro at 0.5.
  This is the act operating point of ADR-0014.
- **Velutina errors come from the Roboflow apiary frames** (37 images, 189 boxes):
  P 0.572, R 0.481, with 68 boxes predicted on background and 98 missed. These frames are
  crowded with small hornets. The iNaturalist velutina photos are few (13 boxes) and only show
  the trend: cc0 P 1.00 / R 0.71, cc-by P 0.17 / R 0.17.
- Confusions between classes are rare: crabro→velutina 3, velutina→crabro 2, velutina→other 5.

## Limits

- **Pre-field only.** test-v1 holds public images. Its bee boxes come from one Sledevic landing
  board. These numbers do **not** pass the M5 gate, which needs field rows (`test-v2`, 2027;
  ADR-0020).
- The comparison is one-sided by design: VespAI has no bee or "other" class.
- Velutina recall (0.48) is the first number to improve. Levers to try: more velutina images
  at the hive entrance, a larger resolution or the Medium size (ADR-0024 D1 sensitivity), and
  choosing a threshold per class (ADR-0014).
