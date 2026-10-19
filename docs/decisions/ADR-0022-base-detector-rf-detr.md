# ADR-0022: RF-DETR (Apache-2.0 sizes) as the base detector of the own model

- Status: Accepted (owner, 2026-10-19)
- Date: 2026-10-19 (issue #95; the "dedicated M5 ADR" announced by ADR-0015)

## Context

ADR-0015 requires a base whose code **and** weights are permissive. Checked 2026-10-19:
RF-DETR (`rfdetr`, Roboflow) — code Apache-2.0; detection weights Nano/Small/Medium/Large
Apache-2.0, other sizes under PML 1.0 (**verified**, README). YOLOX — code Apache-2.0, weights
licence not stated. RT-DETR — code Apache-2.0, weights not stated. D-FINE — Objects365 checkpoints
not commercially cleared. YOLOv9 GPL-3.0; Ultralytics YOLOv8/11 AGPL-3.0: excluded. torchvision
detectors BSD-3 (not re-verified). Hardware: RTX 4070 Laptop 8 GB for training. The M6 target is a
Hailo NPU, whose support for DETR-type models is **unverified** (estimate).

## Options (MCDA)

Script: [`mcda/adr_0018_0022_annotation_pipeline.py`](mcda/adr_0018_0022_annotation_pipeline.py). Scores 0–5, weights /100, totals /500; scores are estimates unless marked verified.

| Option | Licence 30 | Small-data accuracy 25 | Hailo path 20 (estimate) | Training effort 15 | Maturity 10 | Total |
|---|---|---|---|---|---|---|
| A. RF-DETR Small/Medium | 5 | 5 | 2 | 4 | 4 | **415** |
| B. YOLOX-S | 4 | 3 | 5 | 3 | 3 | 370 |
| C. RT-DETR | 4 | 4 | 2 | 3 | 4 | 345 |
| D. torchvision Faster R-CNN | 4 | 3 | 1 | 4 | 5 | 325 |

Sensitivity: Hailo 30 → A 390 = B 390 (tie); Hailo 35 → B 390, A 375 (B leads); licence 40 → A 450.
**Fragile on the edge-deployment weight**: the pre-field model is a research artefact, M6 decides
the edge model on measured Hailo support (YOLOX remains the fallback).

## Decision

- Fine-tune **RF-DETR** (Apache-2.0 sizes only — Nano to Large) from its COCO checkpoint.
- Training lives in `scripts/train_rfdetr.py` plus an optional extra `train`; nothing in the core
  `dependencies` (ADR-0001). Versions pinned after checking current docs at implementation.
- The trained model plugs in as a second `HornetDetector` adapter later (ADR-0015); this brick
  only trains and scores it.
- Weights are git-ignored, loaded from a path, with SHA-256 recorded in the report.

## Consequences

- If Hailo cannot run RF-DETR, M6 retrains YOLOX-S on the same manifest (data is model-agnostic).
