# M5 survey — pre-trained detectors, public datasets and free training GPUs

This survey (2026-11-05, issue #168) prepares M5, the [own vision model](../architecture/specs/own-vision-model.md), before any field data exists. It keeps RF-DETR as the base detector, so ADR-0022 stands. It lists which public data the product can legally use. It plans training on the local GPU, with free cloud GPUs only as overflow.

**How to read the marks.** **V** means the fact was checked on the cited page on 2026-11-05. **E** means an estimate, a vendor claim or a secondary source. Unmarked figures in the tables are vendor-published COCO numbers (E).

**Licence rule (ADR-0015).** Both the code and the weights must be permissive: no non-commercial (NC) licence, no AGPL or GPL in the product.

## 1. Base detectors

| Model | Code / weights licence | Sizes and COCO AP50:95 | Hailo-8L | Fine-tune tooling |
|---|---|---|---|---|
| **RF-DETR** (`rfdetr` 1.11.2, 2026-10-04) | Code Apache-2.0. Weights: N/S/M/L Apache-2.0; Atto/Femto/Pico/XL/2XL under PML 1.0 (`rfdetr[plus]`), **V** ([repo](https://github.com/roboflow/rf-detr)). Objects365 pre-training is inherited from LW-DETR (`rfdetr/datasets/o365.py`); its terms on the weights are unchecked (E) | N 48.4, **S 53.0** (32.1 M parameters), M 54.7, L 56.5 | No compiled result found (E). A Rockchip port runs the transformer head on the CPU | pip package, train/export API, ONNX CPU export (**V**) |
| D-FINE | Apache-2.0. Objects365 checkpoints "may be subject to Objects365 terms" (**V**) | N 42.8 … X 55.8 | Not in the Model Zoo (**V**) | Repo scripts, no pip package |
| DEIM | Apache-2.0 code. Weights licence not stated separately; same Objects365 caveat as D-FINE (E) | N 43.0 … X 56.5 | Not in the Zoo | Same as D-FINE |
| DEIMv2 | Non-commercial weights (**V**) | Atto 23.8 … X 57.8 | — | **Excluded** |
| RT-DETRv2 / v4 | Apache-2.0 code. v4 is distilled from a DINOv3 teacher; the effect on the weights is unchecked (E) | v2: S 48.1 … X 54.3. v4: S 49.8 … X 57.0 | Not in the Zoo | Repo scripts |
| LW-DETR | Apache-2.0, Objects365 pre-training | tiny 42.6 … large 56.1 | Not in the Zoo | No custom-training docs |
| **YOLOX** | Apache-2.0. Weights licence not stated separately (E) | s 40.5, m 46.9 | **Compiled for hailo8l** as `yolox_tiny` (31.4 mAP, 214 FPS) and `yolox_s_leaky` (37.3 mAP, 109 FPS), **V** ([Hailo Model Zoo](https://github.com/hailo-ai/hailo_model_zoo/blob/master/docs/public_models/HAILO8L/HAILO8L_object_detection.rst)). The fallback must be trained in the LeakyReLU variant | Tutorial and ONNX export; last update 2023-02 |
| Ultralytics YOLOv8 / 11 / 26, YOLOv9 | AGPL-3.0 / GPL-3.0 | — | Best Zoo coverage | **Excluded** (licence) |

**Transformer detectors on Hailo-8L.** The only transformer detector compiled for Hailo-8L is `detr_resnet_v1_18_bn` (31.5 mAP, 23 FPS, **V**). DETR-type models can therefore compile, but there is no RT-DETR, D-FINE or RF-DETR entry. That is why all four DETR-family options score 2 on the Hailo path, against 5 for YOLOX.

**Small-object accuracy.** No source publishes AP_small for these models, and no independent small-object comparison was found (E). The vendor comparison (RF-DETR S 53.0 against D-FINE S 50.7) comes from Roboflow itself.

### Insect and hornet pre-trained models

No pre-trained hornet detector usable in a product was found. This comes from searches of the Hugging Face Hub and GitHub (E):

- **VespAI** is CC BY-NC-SA, rejected under ADR-0015.
- **vespCV/hornet3000** (YOLOv10n / YOLOv8s) is a GPL-3.0 repository built on AGPL Ultralytics. Its archive date, 2025-06, comes from search snippets only (E).
- **Ayoubkassi/Asian-hornet-detection** is MIT, but the provenance of its training data is unknown, so it is not reused.
- **Other GitHub hornet repositories** mostly carry no licence, which means all rights are reserved.
- **The Hugging Face Hub** has nothing for *vespa velutina*, *asian hornet* or *vespa crabro*.

The own model therefore stays a fine-tune of a permissive COCO base on our own data.

## 2. Public datasets

| Source | Licence | Content | Use |
|---|---|---|---|
| Sledevič landing-board set (Mendeley 10.17632/8gb9r2yhfc.6) | CC BY 4.0 (**V**, ADR-0021) | 1,453 hive-entrance frames in the manifest | **In use** |
| Roboflow Universe hornet-behavior v1 | CC BY 4.0 (**V**, ADR-0021) | 364 images in the manifest | **In use** (also in `test-v1`) |
| iNaturalist research grade (fetched through the iNaturalist API, ADR-0023) | Per photo; only CC0 and CC BY kept | GBIF occurrence counts with a CC0 or CC BY occurrence licence: *V. velutina* ≈ 9.9 k, *V. crabro* ≈ 13.9 k, *A. mellifera* ≈ 76.9 k (**V**, [GBIF API](https://api.gbif.org/v1/occurrence/search)) | Largest licence-clean reserve (282 images today). Field and macro views, so a domain gap. Filter on the media licence, not the occurrence licence |
| [Zenodo 15622033](https://zenodo.org/records/15622033), honeybee fanning at the hive entrance | CC BY 4.0 (**V**) | About 57.6 k bee instances (E), no hornets | Candidate for the bee class and backgrounds, if it adds viewpoints that the Sledevič set lacks |
| Other Roboflow Universe sets (Hornetino, Asian Hornet Detection, hornet_detection640) | Badge only: CC BY 4.0 or public domain (E, pages not fetchable) | Sizes unknown | Check provenance image by image before any use |
| VespAI data, Hornet3000 (Kaggle), BEEHIVE, SCIBee, NEOPOLL | NC, mixed or unstated | — | Not usable |

**Attribution.** It is a legal grey zone whether a model trained on CC BY photos is a derivative work. The mitigation is attribution:
- the licence register (ADR-0019) records it for each source;
- `inat-attribution.csv` (ADR-0023) records it for each iNaturalist photo.

## 3. Free training compute

| Service | GPU / VRAM | Quota | Session | Checkpointing | Terms for a product |
|---|---|---|---|---|---|
| **Local RTX 4070 Laptop** | 8 GB | Unlimited | Unlimited | Local disk | Data never leaves the machine |
| **Kaggle** | P100 16 GB (**V**). T4 ×2 offered in the UI (E) | 30 h per week, "sometimes higher" (**V**, [GPU tips](https://www.kaggle.com/docs/efficient-gpu-usage)) | 12 h per GPU session, run in the background with "Save & Run All" (**V**, [notebooks doc](https://www.kaggle.com/docs/notebooks)) | `/kaggle/working`, up to 20 GB, reusable as an input (**V**) | Terms not read (E). Keep datasets private |
| **Modal** | T4, L4, A10, A100 (**V**) | 30 $ credit per month (**V**, [pricing](https://modal.com/pricing)), about 37 h of L4 or 27 h of A10 before CPU and RAM charges (E) | Function timeout is configurable (E) | Modal volume | Commercial use of outputs not checked (E) |
| Colab free | T4 typical (E) | Dynamic, unpublished (**V**) | 12 h at most, may stop without notice (**V**) | Google Drive | Bonus only |
| Lightning AI free | T4 / L4 (**V**) | About 30 credits, 25 of them only after adding a card (**V**) | The Studio restarts every 4 h (**V**) | 50 GB persistent | Bonus only |
| Paperspace free, SageMaker Studio Lab, HF ZeroGPU | — | — | — | — | Rejected: public notebooks and a card required / closed to new users / inference only |

**Speed compared with the RTX 4070 Laptop (E).** T4 ≈ 0.4–0.5×, P100 ≈ 0.5×, L4 ≈ 0.6–0.8×, A10 ≈ 1×. The cloud is not faster. Its value is VRAM: 16 to 24 GB is enough for RF-DETR Medium, a larger batch or a higher resolution.

**Data protection.** All these services are hosted in the United States. Before any upload, strip EXIF data (GPS in particular) and any person from the images, and keep the datasets private.

### Run plan (proposal; an ADR is required before the first cloud run)

1. **Default: local.** RF-DETR Small at 512 px stays on the RTX 4070, as in ADR-0024. One run fits in an evening.
2. **Overflow: Kaggle.** Use it for RF-DETR Medium, or for resolution and tiling sweeps that do not fit in 8 GB.
   - Keep each run under 11 h and save a checkpoint every epoch in `/kaggle/working`. Resume by adding that output as a notebook input.
   - Upload a dereferenced copy of the exported YOLO view as a private dataset. The ADR-0024 export is made of symlinks, so copy it with `cp -rL` first. Strip EXIF on that copy.
3. **Burst: Modal.** One L4 or A10 run per month, when a deadline needs it, with checkpoints on a Modal volume.
4. **Accounts.** The owner opens the Kaggle and Modal accounts. Before the first run, read their terms on outputs and private data, then record the decision in an ADR.

## 4. MCDA

The totals are computed by [`../decisions/mcda/research_2026_11_05_m5_models_free_gpus.py`](../decisions/mcda/research_2026_11_05_m5_models_free_gpus.py). The owner validated the weights on 2026-11-05. Scores run from 0 to 5 and totals are out of 500. The scores are estimates built on the facts above. Option letters differ from ADR-0022, where YOLOX-S was option B.

### D1 — base detector

| Option | Licence 30 | Small-data accuracy 25 | Hailo path 20 | Training effort 15 | Maturity 10 | Total |
|---|---|---|---|---|---|---|
| **A. RF-DETR Small/Medium** | 4 | 5 | 2 | 5 | 4 | **400** |
| D. YOLOX-S (`yolox_s_leaky`) | 4 | 3 | 5 | 3 | 3 | 370 |
| C. RT-DETRv2 / v4 | 4 | 4 | 2 | 2 | 4 | 330 |
| B. D-FINE / DEIM | 4 | 4 | 2 | 2 | 3 | 320 |

- **Licence.** Every option scores 4. RF-DETR, D-FINE, DEIM and RT-DETR all carry an unchecked caveat on Objects365 or teacher weights. YOLOX does not state a separate weights licence.
- **A, RF-DETR.** Its pipeline is already trained and scored (ADR-0024), and it has the best tooling.
- **D, YOLOX-S.** It is compiled for Hailo-8L, but it is weaker on small objects and its tooling is stale.
- **B and C.** They have no pip tooling.

**Sensitivity.**

| Weights (licence / accuracy / Hailo / effort / maturity) | Result |
|---|---|
| 30 / 25 / 30 / 10 / 5 | D 390, A 375 (**D leads**) |
| 25 / 20 / 40 / 10 / 5 | D 405, A 350 |
| 40 / 25 / 15 / 10 / 10 | A 405, D 370 |

The ranking is fragile on the edge-deployment weight, as in ADR-0022: it flips as soon as the Hailo path weighs 30. That is M6's measured decision.

**Decision: keep RF-DETR.** ADR-0022 stands, and no new ADR is needed. M6 starts with a check that the RF-DETR ONNX export compiles with the Hailo Dataflow Compiler. YOLOX-S, trained as `yolox_s_leaky`, stays the fallback.

### D2 — training compute

| Option | Zero cost 25 | VRAM / throughput 25 | Terms fit 20 | Session reliability 15 | Setup friction 15 | Total |
|---|---|---|---|---|---|---|
| **A. Local RTX 4070 Laptop 8 GB** | 5 | 3 | 5 | 5 | 5 | **450** |
| B. Kaggle | 5 | 4 | 3 | 4 | 3 | 390 |
| C. Modal | 3 | 5 | 3 | 4 | 3 | 365 |
| D. Colab free | 5 | 4 | 3 | 1 | 4 | 360 |

**Sensitivity.**

| Weights (cost / VRAM / terms / reliability / friction) | Result |
|---|---|
| 20 / 45 / 15 / 10 / 10 | A 410, C 400, B 395 (A leads) |
| 25 / 60 / 5 / 5 / 5 | C 425, B 415, A 380 (cloud leads) |

**Decision: train locally by default.** The cloud is used only for runs that need more than 8 GB, which is where the sensitivity flips.
- **Kaggle comes before Modal**, although Modal leads once throughput dominates. Kaggle's quota renews every week at no cost, while Modal's credit is capped and is billed beyond it.
- **This is a plan.** The cloud ADR comes before the first cloud run.

## 5. Follow-ups

- **M6:** compile the RF-DETR ONNX export with the Hailo Dataflow Compiler on the bench Pi 5 with Hailo-8L.
- **Objects365:** check the Objects365 pre-training terms of RF-DETR and of LW-DETR.
- **Pre-field manifest:** compare Zenodo 15622033 with the Sledevič set before adding it.
- **Before the first cloud run:** read the Kaggle and Modal terms (outputs, private data), then write the cloud-training ADR.
- **Roboflow Universe:** re-check licences image by image, in a signed-in browser, before using any set not yet in the manifest.
- **`references.md`:** re-check the Hornet3000+ and `vespCV/vespcv` licence rows. They are pre-existing and may be stale.

The raw notes of the three searches are kept outside the repository. The facts above are the retained subset.
