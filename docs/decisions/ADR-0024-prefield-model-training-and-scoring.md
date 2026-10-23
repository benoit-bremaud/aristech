# ADR-0024: Train RF-DETR Small on an exported YOLO view, score it through the UC3 harness

- Status: Accepted (owner, 2026-10-23)
- Date: 2026-10-23 (issue #95, PR 4; refines ADR-0022)

## Context

ADR-0022 picks RF-DETR (Apache-2.0 sizes) and puts training in `scripts/train_rfdetr.py` plus
an extra `train`. It leaves three questions open, and the signed gate does not answer them:
which size, how the model is scored next to VespAI, and whether the agent-reviewed iNaturalist
boxes (PR 3) get a human check before training.

Checked 2026-10-23 on PyPI and in the official training docs: `rfdetr` 1.11.2 (2026-10-04),
Apache-2.0, Python ≥ 3.10. Nano, Small and Medium are Apache-2.0; XL and 2XL are PML 1.0.
`model.train(dataset_dir=…)` reads a YOLO layout (`data.yaml`, `train/`, `valid/`) and
`batch_size="auto"` sizes the batch for the GPU. Hardware: RTX 4070 Laptop, 8 GB.

## Options (MCDA)

Script: [`mcda/adr_0024_prefield_training.py`](mcda/adr_0024_prefield_training.py). Scores 0–5,
weights /100, totals /500; scores are estimates.

### D1 — model size

| Option | Small-object accuracy 30 | Fits 8 GB 25 | Training time 20 | Edge path 15 | Licence 10 | Total |
|---|---|---|---|---|---|---|
| A. Nano (384 px) | 2 | 5 | 5 | 5 | 5 | 410 |
| B. Small (512 px) | 4 | 4 | 4 | 4 | 5 | **410** |
| C. Medium | 5 | 3 | 3 | 3 | 5 | 380 |

Sensitivity: accuracy 45 → B 410 = C 410, A 365; edge 30 or memory 40 → A 425, B 410.
**Tie, fragile.** The owner chose B: the pre-field model measures whether we beat VespAI, it is
not the edge model (M6 decides that on measured Hailo support, ADR-0022), and 384 px shrinks the
small hornets of iNaturalist and Roboflow photos.

### D2 — scoring path

| Option | Same yardstick as VespAI 35 | DRY 25 | Reusable later 20 | Effort 20 | Total |
|---|---|---|---|---|---|
| A. `RFDETRDetector` adapter of `HornetDetector` + the UC3 harness | 5 | 5 | 5 | 3 | **460** |
| B. Metrics re-coded in the training script | 3 | 1 | 1 | 4 | 230 |
| C. rfdetr's built-in COCO mAP only | 1 | 4 | 1 | 5 | 255 |

Sensitivity: effort 40 → A 420; reuse 0 → A 440. **Robust.** The adapter is the second
`HornetDetector` implementation announced by ADR-0015, so the port gains its second force.

### D3 — human box check before training

| Option | Label trust 40 | Owner time 30 | Delay 20 | Traceability 10 | Total |
|---|---|---|---|---|---|
| A. Contact sheet of 30 iNaturalist images (10 per class, seeded) | 4 | 4 | 4 | 4 | **400** |
| B. No check | 2 | 5 | 5 | 2 | 350 |
| C. Review all 282 | 5 | 1 | 2 | 5 | 320 |

Sensitivity: trust 60 → A 400, C 390; owner time 50 → A 400, B 380. **Robust.**

## Decision

- **Size**: RF-DETR **Small**, fine-tuned from its COCO checkpoint. Extra `train` pins
  `rfdetr[train]==1.11.2`; nothing enters the core `dependencies`.
- **Training view**: `scripts/dataset.py export` writes a YOLO view of the manifest under a
  git-ignored directory: `train/` and `valid/` link the stored images and labels, and each frozen set gets its own
  folder (`test-v1/`…) with the **committed label snapshot** (the yardstick, ADR-0020).
  Export runs the frozen-set checks first and refuses (exit 2) on any violation (AC5).
- **Scoring**: `infrastructure/vision/rfdetr_detector.py` (lazy import) maps the model's class
  names to `Species`; `scripts/prefield_report.py` scores RF-DETR and VespAI on `test-v1` with the
  UC3 harness and writes one Markdown report with the manifest hash, the frozen-set id and
  digest, the weights SHA-256 and the licences (AC7, AC8).
- **Box check**: before training the owner checks a 30-image contact sheet
  (`qa/tools/box_spot_check.py`); the verdict goes into the QA note.

## Consequences

- The weights stay git-ignored and are loaded from a path; the report records their SHA-256.
- VespAI knows only crabro and velutina: its bee and "other" rows are reported as zero recall,
  as in the M3 report; the comparison that matters is the velutina row.
- If Hailo cannot run RF-DETR, M6 retrains another base on the same export (ADR-0022).
