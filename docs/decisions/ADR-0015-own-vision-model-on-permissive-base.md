# ADR-0015: Own vision model on a permissively licensed pre-trained base

- Status: Accepted
- Date: 2026-10-16 (needs brainstorm, Q4)
- Supersedes: ADR-0002 (VespAI stays wrapped, as the comparison baseline)

## Context

ADR-0002 wrapped VespAI to detect within days. Two facts now block it as the product model:

- **It does not transfer.** On a 364-image Roboflow *V. velutina* / *V. crabro* set (CC BY 4.0),
  *V. velutina* recall is ~0.10 at confidence 0.5 and ~0.03 at 0.8 (~0.13 at the best image size —
the "3–13 %" range quoted elsewhere) (measured 2026-05-23; to be
  made reproducible by the M3 report brick). It under-detects across the set (~1.25 predicted boxes
  per image vs ~5.4 ground-truth).
- **Its licence.** VespAI weights are CC BY-NC-SA 4.0; any fine-tuned derivative inherits the
  non-commercial clause.

Also relevant: the Ultralytics YOLO implementations (YOLOv5, v8, 11) are AGPL-3.0, which would force
the product's source open.

## Options (MCDA)

Criteria and weights: licence freedom 30, accuracy with little data 30, effort 20, edge deployment
(Hailo) 20. Scores 0–5.

| Option | C1 | C2 | C3 | C4 | Total /500 |
|---|---|---|---|---|---|
| A. Fine-tune the VespAI weights | 0 | 4 | 5 | 4 | 300 |
| B. Fine-tune a permissively licensed pre-trained detector (COCO / ImageNet) on own footage + CC BY public data | 5 | 4 | 3 | 4 | **410** |
| C. Train from scratch | 5 | 1 | 1 | 3 | 260 |

Sensitivity (script-checked): with effort at 30 (licence 20), B 390, A 350; A only leads when
licence freedom drops to about 10 (weights 10/30/30/30: A 390, B 380), i.e. no product, ever. **Chosen: B** (owner, 2026-10-16).

## Decision

- aristech trains **its own** detector: a pre-trained base under a permissive licence (Apache-2.0,
  BSD or MIT — candidates such as YOLOX, RT-DETR, torchvision detectors), fine-tuned on own apiary
  footage plus public data under compatible licences (CC BY, CC0; never NC).
- Classes: *V. velutina* (target), *V. crabro* (non-target), honeybee (**explicit class**), other.
- The exact base, its weights' licence and the training stack are chosen in a dedicated M5 ADR,
  with versions checked against current docs.
- It plugs in as a **second adapter of the existing `HornetDetector` port** — no new port.
- VespAI stays as the baseline every own model must beat on the frozen test set (M3).
- VespAI may pre-annotate R&D footage (human-corrected); whether such labels may enter a product
  training set is settled in the M5 ADR.

## Consequences

- M5 moves from "optional fine-tune" to the critical path; it depends on the capture rig and one
  hornet season (ADR-0016, ROADMAP).
- The training stack lives outside the runtime package (or in an optional extra), per ADR-0001.
- The test set is split by day and hive to avoid leakage between training and evaluation.
