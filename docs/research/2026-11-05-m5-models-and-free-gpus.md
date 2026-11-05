# M5 survey — pre-trained detectors, public datasets and free training GPUs

Survey of 2026-11-05 (issue #168) preparing M5 ([own vision model](../architecture/specs/own-vision-model.md))
without field data: it keeps RF-DETR as the base detector (ADR-0022 stands), shortlists the
product-usable public data, and plans training on the local GPU with free cloud GPUs as overflow.

Each fact is marked **V** (verified on the cited page, 2026-11-05) or **E** (estimate, vendor
claim or secondary source). Licence rule: ADR-0015 — code **and** weights permissive, no NC,
no AGPL/GPL in the product.

## 1. Base detectors

| Model | Code / weights licence | Sizes and COCO AP50:95 | Hailo-8L | Fine-tune tooling |
|---|---|---|---|---|
| **RF-DETR** (`rfdetr` 1.11.2, 2026-10-04) | Apache-2.0; weights N/S/M/L Apache-2.0, Atto/Femto/Pico/XL/2XL under PML 1.0 (`rfdetr[plus]`) — **V** [repo](https://github.com/roboflow/rf-detr) | N 48.4, **S 53.0** (32.1 M), M 54.7, L 56.5 (**V**, vendor benchmark) | No compiled result found (**E**); a Rockchip port runs the head on CPU | pip package, train/export API, ONNX CPU export (**V**) |
| D-FINE | Apache-2.0; Objects365 checkpoints "may be subject to Objects365 terms" (**V**) | N 42.8 … X 55.8 | Not in the Model Zoo (**V**) | Repo scripts, no pip package |
| DEIM | As D-FINE (**V**) | N 43.0 … X 56.5 | Not in the Zoo | As D-FINE |
| DEIMv2 | **Non-commercial** weights (**V**) | Atto 23.8 … X 57.8 | — | **Excluded** |
| RT-DETRv2 / v4 | Apache-2.0 code; v4 distilled from a DINOv3 teacher, effect on weights unchecked (**E**) | v2 S 48.1 … X 54.3; v4 S 49.8 … X 57.0 | Not in the Zoo | Repo scripts |
| LW-DETR | Apache-2.0, Objects365 pre-training | tiny 42.6 … large 56.1 | Not in the Zoo | No custom-training docs |
| **YOLOX** | Apache-2.0; weights licence not stated separately (**E**) | s 40.5, m 46.9 | **Compiled for hailo8l**: tiny 31.4 mAP / 214 FPS, s 37.3 / 109 FPS (**V**, [Model Zoo v2.20](https://github.com/hailo-ai/hailo_model_zoo)) | Tutorial, ONNX export; last release 2023 |
| Ultralytics YOLOv8/11/26, YOLOv9 | AGPL-3.0 / GPL-3.0 | — | Best Zoo coverage | **Excluded** (licence) |

- The only transformer detector compiled for Hailo-8L is `detr_resnet_v1_18_bn` (31.5 mAP, 23 FPS,
  **V**): DETR-type models compile, but no RT-DETR / D-FINE / RF-DETR entry exists.
- No source publishes AP_small for these models, and no independent small-object comparison was
  found (**E**). Vendor comparisons (RF-DETR S 53.0 vs D-FINE S 50.7) are Roboflow's own.

### Insect / hornet pre-trained models

No product-usable pre-trained hornet detector exists (**V**, HF Hub, GitHub searches):

- VespAI — CC BY-NC-SA (rejected, ADR-0015).
- vespCV/hornet3000 — YOLOv10n/YOLOv8s, GPL-3.0 repo on AGPL Ultralytics, archived 2025-06.
- Other GitHub hornet repos — mostly no licence (all rights reserved).
- Hugging Face Hub — nothing for *vespa velutina*, *asian hornet* or *vespa crabro*.

The own model therefore stays a fine-tune of a permissive COCO base on our own data.

## 2. Public datasets

| Source | Licence | Content | Use |
|---|---|---|---|
| iNaturalist research-grade via GBIF ([occurrence API](https://api.gbif.org/v1/occurrence/search)) | per photo; CC0 + CC BY only | V. velutina ≈ 9.9 k, V. crabro ≈ 13.9 k, A. mellifera ≈ 76.9 k usable images (**V**, counts 2026-11-05) | Main pre-field source (ADR-0021/0023); field/macro view, domain gap; keep an attribution manifest |
| [Zenodo 15622033](https://zenodo.org/records/15622033) — honeybee fanning at the hive entrance | CC BY 4.0 (**V**) | 57,597 bee instances, no hornets | Bee class and hive-entrance backgrounds — candidate for the next pre-field manifest |
| Roboflow Universe sets (hornet-behavior, Hornetino, Asian Hornet Detection, hornet_detection640) | CC BY 4.0 / public domain as **badged** (**E**, pages not fetchable) | ≈ 1 k images each, mixed views | Only after per-image provenance check; else evaluation reference |
| VespAI data, Hornet3000 Kaggle, BEEHIVE, Vilnius, SCIBee, NEOPOLL | NC, mixed or unstated | — | Not usable |

Whether a model trained on CC BY photos is a derivative work is a legal grey zone; the licence
register of ADR-0019 already records attribution per image, which is the mitigation.

## 3. Free training compute

| Service | GPU / VRAM | Quota | Session | Checkpointing | Terms for a product |
|---|---|---|---|---|---|
| **Local RTX 4070 Laptop** | 8 GB | unlimited | unlimited | local disk | data never leaves the machine |
| **Kaggle** | P100 16 GB (**V**); T4 ×2 offered in the UI (**E**) | 30 h/week, "sometimes higher" (**V**, [GPU tips](https://www.kaggle.com/docs/efficient-gpu-usage)) | 12 h per GPU session, background "Save & Run All" (**V**, [notebooks doc](https://www.kaggle.com/docs/notebooks)) | `/kaggle/working` up to 20 GB, reusable as input (**V**) | ToS not read (**E**); keep datasets private |
| **Modal** | T4, L4, A10, A100 (**V**) | 30 $/month credit (**V**, [pricing](https://modal.com/pricing)) ≈ 37 h L4 or 27 h A10 before CPU/RAM (**E**) | function timeout configurable (**E**) | Modal volume | commercial use of outputs not checked (**E**) |
| Colab free | T4 typical (**E**) | dynamic, unpublished (**V**) | ≤ 12 h, may stop without notice (**V**) | Drive | bonus only |
| Lightning AI free | T4/L4 (**V**) | ≈ 30 credits (**V**) | Studio restarts every 4 h (**V**) | 50 GB persistent | bonus only |
| Paperspace free, SageMaker Studio Lab, HF ZeroGPU | — | — | — | — | rejected (public notebooks + card / closed to new users / inference only) |

Speed versus the RTX 4070 Laptop (**E**): T4 ≈ 0.4–0.5×, P100 ≈ 0.5×, L4 ≈ 0.6–0.8×, A10 ≈ 1×.
The cloud value is VRAM (16–24 GB → RF-DETR Medium, larger batch, higher resolution), not speed.
All services are US-hosted: strip EXIF (GPS) and any person before upload, keep datasets private.

### Run plan

1. **Default — local**: RF-DETR Small at 512 px stays on the RTX 4070 (as ADR-0024); one run
   fits an evening.
2. **Overflow — Kaggle**: RF-DETR Medium or resolution/tiling sweeps that do not fit 8 GB; runs
   under 11 h with a checkpoint per epoch in `/kaggle/working`, resumed as a notebook input;
   private dataset upload of the exported YOLO view (ADR-0024).
3. **Burst — Modal**: one L4/A10 run per month when a deadline needs it, checkpoints on a volume.
4. Before the first cloud run: read the Kaggle and Modal terms on outputs and private data, and
   record the result in the licence register.

## 4. MCDA

Script: [`../decisions/mcda/research_2026_11_05_m5_models_free_gpus.py`](../decisions/mcda/research_2026_11_05_m5_models_free_gpus.py).
Weights validated by the owner on 2026-11-05. Scores 0–5, totals /500; scores are estimates
built on the facts above.

### D1 — base detector

| Option | Licence 30 | Small-data accuracy 25 | Hailo path 20 | Training effort 15 | Maturity 10 | Total |
|---|---|---|---|---|---|---|
| **A. RF-DETR Small/Medium** | 5 | 5 | 2 | 5 | 4 | **430** |
| D. YOLOX-S | 4 | 3 | 5 | 3 | 3 | 370 |
| C. RT-DETRv2 / v4 | 4 | 4 | 1 | 2 | 4 | 310 |
| B. D-FINE / DEIM | 4 | 4 | 1 | 2 | 3 | 300 |

- A: Apache-2.0 sizes verified, pipeline already trained and scored (ADR-0024), pip tooling;
  Hailo unproven.
- D: compiled for Hailo-8L, but weaker small-object accuracy and stale tooling.
- B/C: Objects365 caveat on weights, no pip tooling, no Hailo entry.

Sensitivity: Hailo 30 → A 405, D 390 (A leads); Hailo 40 → D 405, A 375 (**D leads**);
licence 40 → A 445. Same fragility as ADR-0022: the ranking flips only when edge deployment
dominates, which is M6's measured decision.

**Decision: keep RF-DETR (ADR-0022 stands, no new ADR).** Add an early M6 check that the RF-DETR
ONNX export compiles with the Hailo Dataflow Compiler; YOLOX-S stays the fallback.

### D2 — training compute

| Option | Zero cost 25 | VRAM / throughput 25 | Terms fit 20 | Session reliability 15 | Setup friction 15 | Total |
|---|---|---|---|---|---|---|
| **A. Local RTX 4070 Laptop 8 GB** | 5 | 3 | 5 | 5 | 5 | **450** |
| B. Kaggle | 5 | 4 | 3 | 4 | 3 | 390 |
| C. Modal | 3 | 5 | 3 | 4 | 3 | 365 |
| D. Colab free | 5 | 4 | 3 | 1 | 4 | 360 |

Sensitivity: throughput 45 → A 410, C 400, B 395 (A leads); throughput 60 → C 425, B 415, A 380
(cloud leads). **Decision: local by default; Kaggle then Modal only for runs that need more than
8 GB**, which is exactly where the sensitivity flips.

## 5. Follow-ups

- M6: compile RF-DETR ONNX with the Hailo Dataflow Compiler on the bench Pi 5 + Hailo-8L.
- Pre-field manifest: evaluate adding Zenodo 15622033 (CC BY) as bee/background data.
- Before a cloud run: read Kaggle and Modal terms (outputs, private data).
- Re-check Roboflow Universe licences per image in a signed-in browser before any use.

Raw notes of the three searches: kept outside the repository (session notes); the facts above
are the retained, verified subset.
