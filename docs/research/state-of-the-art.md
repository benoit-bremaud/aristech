# State of the Art — Vespa velutina detection and deterrence

**Last updated:** 2026-05-19
**Status:** Draft — first complete pass; expected to be re-run before any
major architectural commitment (the field moves fast).
**Audience:** aristech maintainers, future contributors needing to justify
the technical choices made in the project.
**Companion file:** [references.md](references.md) — centralised
bibliography indexed by domain. Every URL cited in the present document
also lives there, classified, with relevance and notes.

## Purpose

Before committing to an in-house detector or deterrent design, this
document inventories what already exists publicly:

- Datasets, models, and code for Vespa velutina detection.
- Academic results that define the current SOTA (precision, recall,
  latency, hardware footprint).
- Open-source vision-guided turrets and non-lethal deterrents we can
  draw mechanical or software inspiration from.

The document is **descriptive** (what exists) rather than prescriptive
(what we should build) — the prescriptive synthesis lives in
`docs/architecture.md` once decisions are taken from this survey.

Sources surveyed: **Kaggle**, **GitHub** (open-source code), **HAL /
theses.fr / arXiv / journals** (academic), **HuggingFace** (pretrained
models), and **DIY / open turret communities** (Hackaday, Instructables,
research labs).

## Kaggle

### Competitions

| Title                                           | Year      | Notes                                                                                              |
| ----------------------------------------------- | --------- | -------------------------------------------------------------------------------------------------- |
| _No competition dedicated to Vespa velutina_    | —         | —                                                                                                  |
| [iNaturalist FGVC challenges][knat]             | 2017–2021 | Generic fine-grained species recognition. Contains Hymenoptera but **no Vespa velutina** baseline. |

[knat]: https://www.kaggle.com/c/inaturalist-2021

### Datasets

| Title                                                                                                                                 | Size   | Type             | Vespa velutina? | Notes                                                                                                   |
| ------------------------------------------------------------------------------------------------------------------------------------- | ------ | ---------------- | --------------- | ------------------------------------------------------------------------------------------------------- |
| [Hornet3000+][kh3000] (Marco Ry van Dijk, sourced from `waarnemingen.nl`)                                                             | ~3000+ | Object detection | **Yes**         | The only Vespa-velutina-specific dataset on Kaggle. Used downstream by `vespCV/hornet3000` with YOLOv10. |
| [European wasp Vespula vulgaris (KITTI)][kvulg]                                                                                       | n/a    | Object detection | No              | Different species (Vespula vulgaris). Not useful as primary training set.                               |
| [BeeImage Dataset][kbeeimg]                                                                                                           | ~5k    | Classification   | No              | Apis mellifera only, no hornet class. Useful only as negative-class supplement.                         |

[kh3000]: https://www.kaggle.com/datasets/marcoryvandijk/vespa-velutina-v-crabro-vespulina-vulgaris
[kvulg]: https://www.kaggle.com/tegwyntwmffat/european-wasp-vespula-vulgaris-kitti-format
[kbeeimg]: https://www.kaggle.com/datasets/jenny18/honey-bee-annotated-images

### Notebooks

| Title                                                              | Framework               | Approach                            |
| ------------------------------------------------------------------ | ----------------------- | ----------------------------------- |
| [2022 UC Asian Hornet Detection — YOLOv5][knb1] (lucaordronneau)   | PyTorch / YOLOv5        | Object detection on Hornet3000+     |
| [Asian Hornet Detection — Swin Transformer / MMDet][knb2] (johanmoncouti) | PyTorch / MMDetection + Swin-T | Transformer-based object detection |

[knb1]: https://www.kaggle.com/code/lucaordronneau/2022-uc-asianhornetdetection-yolov5
[knb2]: https://www.kaggle.com/code/johanmoncouti/asian-hornet-detection-swin-transformer-mmdet

### Kaggle — synthesis

Kaggle's Vespa velutina coverage is **minimal**: one dataset
(Hornet3000+, Dutch citizen-science origin) and two 2022 notebooks
applying YOLOv5 and Swin-T to it. No competition. No French/INRAE/MNHN
dataset despite France being the most-affected country — that material
lives elsewhere (`data.gouv.fr`, GBIF, MNHN's `frelonasiatique.mnhn.fr`).
**Do not lean on Kaggle as the primary source**; treat Hornet3000+ as a
useful starter and look to GitHub + Roboflow Universe for the real
reference datasets.

## GitHub

### Vespa velutina / Asian hornet repos

| Repo                                                                       | License           | Framework             | Approach                                  | Weights | Integration-ready?                                                                  |
| -------------------------------------------------------------------------- | ----------------- | --------------------- | ----------------------------------------- | ------- | ----------------------------------------------------------------------------------- |
| [andrw3000/vespai][gvespai] (VespAI, Univ. Exeter — Nature Comms Bio 2024) | **CC BY-NC-SA 4.0** | PyTorch / YOLOv5s + ResNet | Detection at standardised bait station    | **Yes** | Research-only: NC licence blocks any commercial integration. PR ≥ 0.99 in paper.    |
| [vespCV/vespcv][gvespcv]                                                   | **GPL-3.0**       | Ultralytics YOLOv11s  | Real-time detection on Raspberry Pi 4     | Implied | Closest production-grade Python+Pi stack but GPL is **viral** — would force aristech to GPL. |
| [vespCV/hornet3000][gh3000]                                                | GPL-3.0           | YOLOv10n              | Detection, Pi 4 + Arducam, Colab-trained  | Yes     | More of a tutorial / how-to than a library.                                         |
| [vespCV/gv2-esp32][gvgrove]                                                | not confirmed     | YOLO11n on Grove Vision AI V2 | On-device                              | Yes     | Hardware-specific to ESP32-S3 + Grove board.                                        |
| [lbrejon/Localization-of-Asian-hornets…][gbrejon]                          | undeclared        | PyTorch (ResNet18 + CAM) | Classification + CAM localisation         | unclear | Student-style, no licence, not usable in production.                                |
| [Jodaille/Jobee][gjobee]                                                   | undeclared        | OpenCV (no ML)        | Heuristic orange-tail colour detection    | n/a     | Hobby baseline. Useful only as a colour-based prefilter.                            |
| [Barrois/Detecteur-ESP32-Cam-Blob-Detector][gbarrois]                      | undeclared        | C++ on ESP32-CAM      | Hover-detect + photo capture, acoustic trigger | n/a | Hardware project, not a Python lib.                                                 |

[gvespai]: https://github.com/andrw3000/vespai
[gvespcv]: https://github.com/vespCV/vespcv
[gh3000]: https://github.com/vespCV/hornet3000
[gvgrove]: https://github.com/vespCV/gv2-esp32
[gbrejon]: https://github.com/lbrejon/Localization-of-Asian-hornets-with-CNN-using-CAM
[gjobee]: https://github.com/Jodaille/Jobee
[gbarrois]: https://github.com/Barrois/Detecteur-ESP32-Cam-Blob-Detector

### Adjacent repos (apiary IoT, bee tracking, insect detection)

| Repo                             | Relevance | Why useful                                                                                                                 |
| -------------------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------- |
| [BeeAlarmed/BeeAlarmed][gba1]    | **High**  | Camera + TF/OpenCV pipeline already classifying bees vs **wasps**, pollen, varroa. Transfer-learn to add Vespa velutina.   |
| [BeeAlarmed/BeeDataset][gba2]    | **High**  | Published TFDS multi-label bee dataset — directly reusable for pretraining.                                                |
| [Mjrovai/Bee-Counting][gmjr]     | Medium    | YOLOv8 → NCNN on Raspberry Pi Zero 2W. Good template for the edge-deployment side of aristech.                              |
| [matpalm/bnn][gmatp]             | Medium    | U-Net bee-position bitmap on Pi + Intel NCS / JeVois. Semi-supervised pattern worth borrowing.                              |
| [t9s9/BeeMeter][gbm]             | Medium    | CNN detection + multi-frame tracking to a counting zone. Pattern transferable to hornet ingress counting.                   |
| [Gratheon/models-gate-tracker][ggrat] | Medium | Maintained fork of BeeAlarmed focused on hive-entrance tracking.                                                            |

[gba1]: https://github.com/BeeAlarmed/BeeAlarmed
[gba2]: https://github.com/BeeAlarmed/BeeDataset
[gmjr]: https://github.com/Mjrovai/Bee-Counting
[gmatp]: https://github.com/matpalm/bnn
[gbm]: https://github.com/t9s9/BeeMeter
[ggrat]: https://github.com/Gratheon/models-gate-tracker

### French / EU sources

| Org / Project                                          | What it provides                                                                              |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| [MNHN — Frelon Asiatique (INPN)][fmnhn]                | National citizen-science reporting portal. Canonical sighting database (no detection code).   |
| [INPN Espèces app][finpn]                              | Species reporting + observation app from MNHN.                                                |
| [SignalNids][fsign]                                    | Web app to declare nests + view the map. Community-run.                                       |
| [INRAE][finrae]                                        | Original radio-tag tracking research (not open-source detection code). Agiir reporting app.   |
| [LOCNEST][flocnest]                                    | **Open-source 3D-printable hornet-tracking hardware** (KissKissBankBank-funded).              |
| [Roboflow Universe — Asian Hornet Detection][froboflow] | Labelled image datasets (~711+ images) reusable for fine-tuning. Strong overlap with Hornet3000+. |

[fmnhn]: https://frelonasiatique.mnhn.fr/
[finpn]: https://inpn.mnhn.fr/espece/cd_nom/433589
[fsign]: https://signalnids.fr/
[finrae]: https://www.inrae.fr/
[flocnest]: https://www.kisskissbankbank.com/en/projects/locnest-une-solution-libre-pour-localiser-les-nids-de-frelons-asiatiques
[froboflow]: https://universe.roboflow.com/use-case-asian-hornet-detection/asian-hornet-detection-a6ael

### GitHub — synthesis

The open-source ecosystem for Vespa velutina detection is **emerging
but immature**:

- Only one peer-reviewed system with published weights exists (**VespAI**),
  and its CC BY-NC-SA licence forbids commercial use.
- The most active practical work is the **vespCV** organisation, all
  GPL-3.0 — would force aristech itself to become GPL if vendored. Its
  training dataset is **not shared** (code + a pretrained YOLOv11s model
  only; images were sourced from `waarnemingen.nl`). _M1 finding._
- A Roboflow Universe set with an explicit three-class labelling
  (**bee / _V. crabro_ / _V. velutina_**, ~118 images, `to-verify` exact
  URL + licence) is the most direct seed for the deferred explicit-bee
  class (the M5 fine-tune) — most other sets label only the two hornet
  species. _M1 finding._
- The richest _engineering_ prior art is actually adjacent: **BeeAlarmed**
  (TF, multi-class incl. wasps, mature) plus its TFDS dataset, and
  **Mjrovai/Bee-Counting** for the YOLOv8 → Raspberry Pi edge pattern.
- French sources (MNHN, INRAE, INPN) provide sighting data but no
  open-source detection code as of this survey.
- **LOCNEST** is directly relevant to aristech's hardware ambitions
  (open-source nest tracker) and deserves a dedicated look.

**Pragmatic path**: pretrain on the **BeeAlarmed dataset + Roboflow "Asian
Hornet Detection" set** (~3k images after dedup), borrow VespAI's
architecture (YOLOv5s + ResNet) as a _reference_ implementation, and
keep aristech's own code permissively licensed by reimplementing the
detector rather than vendoring GPL/NC code.

## Academic papers

### Vision-based detection

| Title                                                                                                  | Year | Venue                          | Approach                                          | Metric                                  | Code?                  |
| ------------------------------------------------------------------------------------------------------ | ---- | ------------------------------ | ------------------------------------------------- | --------------------------------------- | ---------------------- |
| [VespAI: a deep learning-based system for the detection of invasive hornets][p1]                       | 2024 | Nature Communications Biology  | YOLOv5s + ResNet backbone on a Raspberry Pi 4 monitoring station, motion-triggered | Mean precision-recall **≥ 0.99**        | Yes ([andrw3000/vespai][gvespai]) |
| [Deep Learning-Based Portable Image Analysis System for Real-Time Detection of Vespa velutina][p2] (Kim et al.) | 2023 | MDPI Applied Sciences 13(13):7414 | Improved YOLOv5s portable real-time system        | 83.3% detection rate over 3-hive field test | No                     |
| [Improving Hornet Detection with the YOLOv7-Tiny Model][p3]                                            | 2025 | Computers, Materials & Continua | YOLOv7-Tiny variant for lightweight edge inference | Reported gains over baseline YOLOv7-Tiny | No public link surfaced |
| [Détection, caractérisation et quantification des attaques de frelon asiatique…][p4]                   | 2021 | Conf. IA & Biodiversité (HAL-INRAE hal-03258615) | Deep learning + video surveillance at hive entrance (FR) | Qualitative / preliminary               | No                     |
| [Method for Nest Detection of the Yellow-Legged Hornet in High Density Areas][p5]                      | 2024 | Insects / MDPI                 | Aerial/ground nest detection (not individual hornets) | Nest-level metrics                      | No                     |

[p1]: https://www.nature.com/articles/s42003-024-05979-z
[p2]: https://www.mdpi.com/2076-3417/13/13/7414
[p3]: https://www.techscience.com/cmc/v83n2/60597/html
[p4]: https://hal.inrae.fr/hal-03258615
[p5]: https://pmc.ncbi.nlm.nih.gov/articles/PMC10926382/

### Acoustic detection

| Title                                                                                                                       | Year | Venue                                  | Approach                                                              | Metric                                                | Code? |
| --------------------------------------------------------------------------------------------------------------------------- | ---- | -------------------------------------- | --------------------------------------------------------------------- | ----------------------------------------------------- | ----- |
| [Remote and automated detection of Asian hornets… using spectral features of their hovering flight sounds][p6] (Hall et al.) | 2025 | Computers and Electronics in Agriculture 235:110307 | Microphones + PCA + Discriminant Function Analysis on hovering spectra | **98.7% accuracy** on ~1 h of apiary recordings; single-individual sensitivity | No |
| [Automated detection of the yellow-legged hornet using an optical sensor with machine learning][p7] (Herrera et al.)         | 2023 | Pest Management Science (Wiley)        | Irideon optoacoustic wingbeat sensor + ML, 14-value PSD features      | 80.1 ± 13.9% mean species accuracy; 74.5 ± 7.0% for V. velutina; F1 ≈ 80% | Proprietary sensor |

[p6]: https://www.sciencedirect.com/science/article/pii/S0168169925004132
[p7]: https://scijournals.onlinelibrary.wiley.com/doi/full/10.1002/ps.7296

### Multimodal (vision + audio)

**No peer-reviewed paper found that combines vision and audio for
Vespa velutina.** This is a gap in the literature and a potential niche
for original work — vision provides species discrimination and bbox
localisation, audio provides cheap omnidirectional always-on detection
of the characteristic hovering pattern.

## HuggingFace

### Hornet / bee-specific models

| Model                                                | Architecture                          | Training data        | Vespa velutina class?                                | URL          |
| ---------------------------------------------------- | ------------------------------------- | -------------------- | ----------------------------------------------------- | ------------ |
| [Honey-Bee-Society/honeybee_ml_v1][hf1]              | AutoGluon MultiModalPredictor         | ~70k iNaturalist images | Coarse "Vespidae" class only — not species-level     | model card   |
| [MuGeminorum/insecta][hf2] (mirror Genius-Society/insecta) | Object detection over 2 037 insect taxa | iNaturalist-derived | Likely species-level — verify before relying          | model card   |
| [mnauf/detect-bees Space][hf3]                       | YOLO-family demo                      | Demo                 | No                                                    | space        |

[hf1]: https://huggingface.co/Honey-Bee-Society/honeybee_ml_v1
[hf2]: https://huggingface.co/MuGeminorum/insecta
[hf3]: https://huggingface.co/spaces/mnauf/detect-bees

**No HuggingFace model is explicitly trained on Vespa velutina with
declared license and weights.** The best species-specific weights live
on GitHub (vespCV org).

### Recommended pretrained backbones for fine-tuning

| Backbone                  | Why                                                                                                 | License           |
| ------------------------- | --------------------------------------------------------------------------------------------------- | ----------------- |
| [Ultralytics YOLOv8n/s][b1]   | Strong small-object performance, mature ONNX/TFLite/Edge TPU export, large fine-tune community.    | **AGPL-3.0**      |
| [YOLOv10n][b2]            | Lower-latency NMS-free head; already proven on Raspberry Pi for V. velutina (`vespCV/hornet3000`).   | AGPL-3.0          |
| [YOLOv9-c][b3]            | Best mAP/latency tradeoff among the YOLO line at small-object scales.                                | GPL-3.0           |
| [RT-DETR / RF-DETR][b4]   | Transformer-based, no NMS, strong on cluttered hive entrances.                                       | Apache-2.0        |
| [Grounding-DINO][b5] (Swin-T) | Open-vocabulary detector — zero-shot pre-labelling ("yellow-legged hornet") before any labels. mIoU 0.642 vs 0.503 for YOLO-World in ecology benchmarks. | Apache-2.0        |
| [YOLO-World][b6]          | Real-time open-vocabulary YOLOv8-based — fastest path to a pre-labelling pipeline.                   | GPL-3.0           |

[b1]: https://docs.ultralytics.com
[b2]: https://github.com/THU-MIG/yolov10
[b3]: https://github.com/WongKinYiu/yolov9
[b4]: https://huggingface.co/PekingU/rtdetr_r50vd
[b5]: https://huggingface.co/IDEA-Research/grounding-dino-tiny
[b6]: https://huggingface.co/spaces/stevengrove/YOLO-World

### Academic + HuggingFace — synthesis

The field is **sparse but converging**:

- The only peer-reviewed system with near-deployment-grade numbers is
  **VespAI** (PR ≥ 0.99 on a standardised platform — the score reflects
  controlled imaging, not arbitrary apiary footage).
- The Korean MDPI 2023 work and the 2025 YOLOv7-Tiny paper confirm that
  **vanilla YOLO fine-tuned on ~2 k labelled hornet images is the
  de-facto vision SOTA**.
- For acoustic detection, **Hall et al. 2025** is the strongest single-
  sensor result (98.7%) and is genuinely complementary to vision. No
  public code or dataset was located.
- **Open multimodal niche**: no public vision-plus-audio baseline exists,
  which is exactly the architecture aristech is positioned to build.

**Honest gaps** (data quality caveat — most paper-level facts come from
search snippets and abstracts, not full-text reads): VespAI's weights /
dataset visibility on HF or canonical mirrors was not confirmed; numbers
(mAP, PR, dataset size) should be re-verified by reading the PDFs before
quoting them in design documents.

## Auto-aim turrets and non-lethal deterrents

### Vision-guided turret projects

| Project                                                    | Stack                           | Tracking algo                       | Actuator                         | License        | Activity      |
| ---------------------------------------------------------- | ------------------------------- | ----------------------------------- | -------------------------------- | -------------- | ------------- |
| [Project Sentry Gun][t1] (Rudolph Labs)                   | Processing + Arduino + OpenCV   | Frame-differencing / background sub | Airsoft / paintball / water gun  | OSS, no SPDX   | Legacy        |
| [HackerShack Tracking-Turret][t2]                         | Python + Raspberry Pi + OpenCV  | Motion detection + centroid         | Nerf flywheel                    | Unlicensed     | Stale         |
| [anjrew/Autonomous-Nerf-Turret][t3]                       | Python + YOLO + OpenCV          | YOLO + centroid PID                 | Nerf                             | **MIT**        | Maintained    |
| [dhairyamishra/NERF_OPENCV_turret][t4]                    | Python + Arduino + FastAPI      | OpenCV + PID, trapezoidal motion    | Nerf burst-fire                  | No SPDX        | Recent        |
| [KevyVo/3D-Printed-AI-Nerf-Sentry-Turret][t5]             | OpenCV + 3D-printed chassis     | OpenCV face tracking                | Nerf                             | Undeclared     | Recent        |
| [rjean/tracker][t6]                                       | Coral Edge TPU + MobileNet-SSD  | DNN detection + centroid            | Generic pan/tilt                 | Undeclared     | Stale         |
| [chenalan02/LaserPointerMotionDetection][t7]              | OpenCV background subtraction   | Motion bg-sub                       | 5 mW laser pointer               | Undeclared     | Stale         |
| [PaintCam Eve][t8] (OZ-IT, Slovenia)                      | Closed source                   | Face recognition + AI               | Paintball / teargas              | Proprietary    | Active product |

[t1]: https://github.com/sentryGun53/Project-Sentry-Gun
[t2]: https://github.com/HackerShackOfficial/Tracking-Turret
[t3]: https://github.com/anjrew/Autonomous-Nerf-Turret
[t4]: https://github.com/dhairyamishra/NERF_OPENCV_turret
[t5]: https://github.com/KevyVo/3D-Printed-AI-Nerf-Sentry-Turret
[t6]: https://github.com/rjean/tracker
[t7]: https://github.com/chenalan02/LaserPointerMotionDetection
[t8]: https://www.paintcam.net/

**Note**: most use **OpenCV motion detection or YOLO + centroid PID** on a 2-DOF servo. **None target insects**; all aim at human-sized objects (~30 cm bbox, 200+ px). A hornet at 1-2 m is 30-60 px — different problem.

### Animal deterrent — mechanical / fluid path

| Product / Project                                       | Mechanism                              | Range            | Pump / nozzle                              | Trigger             |
| ------------------------------------------------------- | -------------------------------------- | ---------------- | ------------------------------------------ | ------------------- |
| [Orbit Yard Enforcer 62100][d1]                         | Impact sprinkler on garden-hose pressure | 10-21 m (33-70 ft) | Hose-fed (~3 bar), impact head, 3-5 s burst | 120° PIR, ~12 m   |
| [Bird-X Hydro Critter Blaster][d2]                      | Solar PIR-triggered sprinkler           | ~11 m            | Hose pattern, solar PIR                    | PIR motion          |
| [DIY 12V diaphragm pump kits][d3] (BD-07W class)        | 12V pump + 12V solenoid + nozzle        | 1-5 m at 7-10 bar | ~1-4.5 L/min, adjustable jet/cone         | GPIO / relay        |

[d1]: https://www.orbitonline.com/products/yard-enforcer-motion-activated-sprinkler
[d2]: https://bird-x.com/bird-products/hydro-critter-blaster/
[d3]: https://bodenpump.com/product/bd-07w-12v-24v-mini-diaphragm-water-pumps-water-purifier-pump-brush/

**Note**: commercial PIR sprinklers are **untargeted area-burst** devices — they cannot discriminate hornet from bee. The fluid path is reusable; the trigger logic is not. A 12V diaphragm pump @ 7-10 bar driving a small solenoid + pencil-jet nozzle is the standard DIY recipe for a directed, pulsed jet at 1-3 m.

### Insect-specific tracking and aim — the closest prior art

| Project                                                                 | Target              | Performance                                                      | Code?                                            |
| ----------------------------------------------------------------------- | ------------------- | ---------------------------------------------------------------- | ------------------------------------------------ |
| [Photonic Fence][i1] (Intellectual Ventures / Photonic Sentry, 2020)    | Mosquitoes          | **25 ms pulse, <2 px mean tracking error**, tested at 2 m and 30 m; ♂/♀ discrimination 96.5% via wingbeat; spares orchid bees | Closed (patents US8705017B2, US20100186284A1) |
| [Ildaron/Laser_control][i2]                                             | Mosquitoes / pests  | Jetson Nano + YOLOv4-tiny: 24-35 FPS                              | Public, no SPDX                                  |
| [mcoates12/autonomous-mosquito-turret][i3]                              | Mosquitoes          | Stereo + servo prototype                                          | Public, undeclared                               |
| [Nassif101/Mosquito-Laser-Defence-Turret][i4]                           | Mosquitoes          | Embedded real-time, vision-guided laser                           | Public                                           |
| VespAI (see Academic papers)                                            | _V. velutina_       | Pi 4, YOLOv5s + ResNet, **mAP ≥0.99**. Output classes _V. velutina_ + _V. crabro_ only — no positive bee class; trained to reject visually similar insects incl. _A. mellifera_ (M0 finding) | Yes (CC BY-NC-SA) |
| [vespCV/gv2-esp32][i5]                                                  | _V. velutina_       | ESP32-S3 + Grove Vision AI V2, detection + relay output (explicitly designed to drive a harp / deterrent) | Yes (GPL-3.0) |

[i1]: https://www.nature.com/articles/s41598-020-71824-y
[i2]: https://github.com/Ildaron/Laser_control
[i3]: https://github.com/mcoates12/autonomous-mosquito-turret
[i4]: https://github.com/Nassif101/Mosquito-Laser-Defence-Turret
[i5]: https://github.com/vespCV/gv2-esp32

**Critical finding**: Photonic Fence is the **only published system** that proves a small flying insect can be hit by a steerable beam at metre-scale with <2 px tracking error and 25 ms pulse — but it uses **galvanometer mirrors**, not servos, and it's patent-encumbered. **No prior art combines insect-class detection with a water jet actuator.** That's the aristech niche.

### Small-fast-target tracking algorithms (Python-ready)

| Algorithm      | Strength                                                 | Weakness                              | License       | Library                                  |
| -------------- | -------------------------------------------------------- | ------------------------------------- | ------------- | ---------------------------------------- |
| MOSSE          | Fastest correlation filter (~hundreds FPS)               | Low accuracy, no scale                | BSD (OpenCV)  | `cv2.legacy.TrackerMOSSE_create`         |
| KCF            | Fast, decent accuracy                                    | Loses target on fast motion / occlusion | BSD (OpenCV)  | `cv2.legacy.TrackerKCF_create`           |
| CSRT           | Best single-object accuracy in OpenCV                    | ~25 FPS                               | BSD (OpenCV)  | `cv2.legacy.TrackerCSRT_create`          |
| [ByteTrack][a1] | Robust multi-object tracking, low-conf box association  | Needs a detector per frame            | MIT           | `FoundationVision/ByteTrack`             |
| [OC-SORT][a2]  | Robust to occlusion / non-linear motion (hornet hover)   | Detector-dependent                    | MIT           | `noahcao/OC_SORT`                        |
| Kalman + Hungarian (SORT-style) | Trivial, predictable                    | Needs sustained 30+ FPS detection     | MIT (filterpy) | `filterpy` + custom                     |
| [Roboflow `trackers`][a3] | SORT/ByteTrack/OC-SORT/BoT-SORT under one API | Newer, fewer benchmarks             | Apache-2.0    | `pip install trackers`                   |

[a1]: https://github.com/FoundationVision/ByteTrack
[a2]: https://github.com/noahcao/OC_SORT
[a3]: https://github.com/roboflow/trackers

**Recommendation**: YOLO detector + **OC-SORT or ByteTrack** for ID continuity, with a Kalman one-step lookahead to compensate for the actuator + ballistic delay (~50 ms).

### Pan/tilt mechanical platforms

| Platform                                              | Resolution                    | Backlash             | Price          | Notes                                                                              |
| ----------------------------------------------------- | ----------------------------- | -------------------- | -------------- | ---------------------------------------------------------------------------------- |
| Adafruit Mini Pan-Tilt (SG90 micro-servos)            | ~1° (servo PWM step)          | High (1-3°)          | ~€20           | Adequate for face tracking, **marginal for 30-60 px target at 2 m**.              |
| Pimoroni Pan-Tilt HAT                                 | Same SG90-class               | Same                 | ~€25           | Pi HAT, proprietary PWM driver.                                                    |
| MG996R metal-gear servo                               | ~0.3° claimed                 | ~0.5° typical        | ~€10/servo     | Better repeatability, needs external PCA9685.                                       |
| iPower / iFlight gimbal BLDC + AS5048A magnetic encoder (GM3506, GM4108) | **0.022° (14-bit)**, ~0.05° after averaging | Near-zero (direct drive) | ~€50/axis + driver | Standard precision option (SimpleBGC firmware); right tier if water-jet ballistic compensation matters. |

**Servo-class gimbals are sufficient to centre a hornet-sized blob within ~2-3 px error**; BLDC + AS5048A is overkill unless the water jet has a tight ballistic envelope at >2 m.

### Ballistic / water-jet aiming

| Source                                                                                              | Insight                                                                                          |
| --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| [Hu et al., Two-Stage Water Jet Landing Point Prediction, Sensors 2021][w1]                        | CV-based landing-point regression for firefighting robots; jet model = parabolic + drag + wind   |
| [Improved Near-Field CV for Jet Trajectory, Sensors 2020][w2]                                       | Particle-kinematics ballistic model + image-based closed-loop correction                          |
| [UAV-imagery Jet Trajectory Detection, Sensors 2024][w3]                                            | Learnable prompt vectors to segment jet stream                                                    |
| [Study on Water Jet Trajectory Model of Fire Monitor, 2018][w4]                                     | Closed-form parabolic + drag equations, validated experimentally                                  |
| [Self-Choreographed Musical Fountain System][w5]                                                    | Pi + Arduino + PCA9685 + valve drivers — OSC-style synchronised water control (plumbing reference) |

[w1]: https://www.mdpi.com/1424-8220/21/8/2704/htm
[w2]: https://www.mdpi.com/1424-8220/20/24/7029
[w3]: https://www.mdpi.com/1424-8220/24/11/3553
[w4]: https://www.researchgate.net/publication/329571016
[w5]: https://www.researchgate.net/publication/312276164

**Takeaway**: water ballistics for fire monitors are a **solved closed-form problem** (parabolic + quadratic drag). The only domain-specific work needed is a 1D depth estimate of the hornet (stereo or known geometry — hornets fly within a known volume in front of the hive board) and a lookup-table mapping `(pan, tilt, distance) → solenoid open-time`.

### Auto-aim turrets — synthesis and safety

**State of the field**: no published or open-source project combines insect-class vision detection with a water-jet actuator. The two halves exist separately:

- **VespAI / vespCV** prove that _V. velutina_ vs _A. mellifera_ discrimination is ≥99% accurate on a Raspberry Pi 4.
- **Photonic Fence** (Nature Sci. Rep. 2020) proves an insect at 2-30 m can be hit by a steerable beam with 25 ms pulse and <2 px tracking error — but using **galvanometers + laser**, not servos + water.
- **Civilian DIY turrets** aim at human-sized targets with OpenCV + servo PID and would all fail on a 30-60 px hornet without a custom detector.
- **Animal-deterrent sprinklers** (Orbit, Bird-X) have a usable fluid path but no discrimination — they would soak the bee colony along with the hornet.

**Safety / ethics gotchas — flag before any prototype**:

1. **Mis-aim sprays the colony**: bees cannot fly wet. A soaked frame at the hive entrance is a direct welfare hit. Require a hard **geometric exclusion zone** around the landing board, not just a classifier confidence threshold.
2. **High-pressure jets injure insects unintentionally** — "non-lethal" is a function of **pressure × nozzle**: keep below ~3-4 bar with a diffuse jet. A 110 PSI (~7.5 bar) pump on a pinhole nozzle is a cutting jet at 50 cm.
3. **EU/FR regulation** — no EU-wide regulation specifically governs automated apiary deterrents, but the Convention de Berne and French rules on _V. velutina_ (classified _espèce exotique envahissante_ / nuisible sanitaire) allow non-chemical control. Record-keeping of which species was sprayed is the defensible posture. See the **Legal framework** section below for the detailed article-level analysis.
4. **Failure-safe defaults**: pump must be **normally-closed solenoid**, dead-man timer, classifier confidence floor (≥0.9 for hornet, abort if any _Apis_ box overlaps the firing cone).

### Recommended starter stack — minimum viable prototype

- **Detection**: YOLOv8n or VespAI-style YOLOv5s fine-tuned on _V. velutina_ vs _A. mellifera_ (vespCV dataset = obvious starting corpus), on Raspberry Pi 5 + Hailo-8L or Jetson Orin Nano.
- **Tracking**: OC-SORT (MIT) on top of detections, with a 1-step Kalman lookahead to absorb the ~50 ms actuator + ballistic delay.
- **Mechanics v1**: 2x MG996R metal-gear servos on a PCA9685 driver (€30 total). **Mechanics v2**: GM3506 + AS5048A if jitter dominates error budget.
- **Fluid path**: 12V BD-07W-class diaphragm pump regulated to ~3 bar, normally-closed 12V solenoid, pencil-jet nozzle, **~50-200 ms pulse, ~10-30 mL per shot**.
- **Aiming model**: parabolic ballistic lookup table calibrated on a checkerboard at 1.0 / 1.5 / 2.0 / 2.5 m, indexed by image-plane `(u, v)`; refine with Sensors-2021 closed-loop correction once a jet-visible camera is added.
- **Safeguards**: geometric "no-spray" mask drawn around the hive entrance face; abort if any _Apis_ box within N× the hornet bounding box; rolling video log of every shot for post-hoc audit.

## Legal framework (France / EU)

### French legal texts in force

| Reference                                                       | Date           | Effect on Vespa velutina                                                                                                                                                                                                                                                                                       |
| --------------------------------------------------------------- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Arrêté du 26 décembre 2012][l1] (NOR : AGRG1241096A)           | 26 Dec 2012    | Classifies _Vespa velutina nigrithorax_ as **danger sanitaire de deuxième catégorie** for _Apis mellifera_ on the national territory. Still in force, no amendments.                                                                                                                                          |
| [LOI n° 2016-1087 du 8 août 2016][l2] (reconquête biodiversité) | 8 Aug 2016     | Transposes EU Reg. 1143/2014. Creates **Art. L411-5** (introduction in natural env. forbidden), **L411-6** (detention/transport/sale forbidden), **L411-7** (control measures), **L411-8** (mandatory destruction), **L415-3** (criminal penalties).                                                          |
| Décret n° 2017-595 du 21 avril 2017                              | 21 Apr 2017    | Application decree for L411-5/6/7.                                                                                                                                                                                                                                                                            |
| [Arrêté du 14 février 2018][l3]                                  | 14 Feb 2018    | Annex II lists _V. velutina nigrithorax_. Forbids introduction, transit, release, detention, transport, sale, purchase of live specimens. **Note**: this is an _arrêté_, not a _décret_ — common confusion in popular references.                                                                              |
| [Arrêté du 2 mars 2023][l4]                                      | 2 Mar 2023     | Updates EEE list; _V. velutina_ remains listed.                                                                                                                                                                                                                                                                |
| [Arrêté du 23 avril 2007 — insectes protégés][l5]                | 23 Apr 2007    | Lists protected insects (some wild bees, _Bombus_ spp. via regional arrêtés, other pollinators). **Critical for aristech**: any trap killing a protected pollinator triggers **L415-3** (3 years prison + 150 000 €).                                                                                          |
| [Code rural et de la pêche maritime — Art. L211-1, L211-6/7][l8] | consolidated   | Honey bees considered _cheptel_; mandatory annual hive declaration; préfectoral arrêtés set minimum distances.                                                                                                                                                                                                  |

[l1]: https://www.legifrance.gouv.fr/loda/id/JORFTEXT000026844543
[l2]: https://www.legifrance.gouv.fr/loda/id/JORFTEXT000033016237
[l3]: https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000036629851
[l4]: https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000047411674
[l5]: https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000465500
[l8]: https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006071367/

### Recent additions (2022-2026)

| Reference                                            | Date                              | Key provisions                                                                                                                                                                                                                                                                                                                                                                                                  | Status      |
| ---------------------------------------------------- | --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| [LOI n° 2025-237 du 14 mars 2025][l6] (prolifération) | 14 Mar 2025 (JO 15 Mar)           | Inserts **Art. L411-9-1** Code env.: creates a **Plan national de lutte contre le frelon asiatique à pattes jaunes** (national + departmental plans, surveillance, prevention, **selective trapping**, nest destruction, classification of departments by predation pressure, reporting via the _maire_). Inserts **L411-9-2**: economic losses to apiarists indemnified under Art. L361-3 Code rural. No dedicated funding by the law itself. | **En vigueur** |
| [Décret n° 2025-1377 du 29 décembre 2025][l7]         | 29 Dec 2025 (JO 30 Dec)           | Application decree for 2025-237: adoption procedure, consultation list (OVS, élus locaux, OFB, scientifiques, apiculteurs, associations env.). Reinforces that **only selective traps** are recommended.                                                                                                                                                                                                       | **En vigueur** |

[l6]: https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000051329052
[l7]: https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000053201550

The law the user remembered is **Loi n° 2025-237 du 14 mars 2025** — promulgated ~14 months ago at time of writing.

### EU framework

| Reference                                                 | Effect                                                                                                                                          |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [Règlement (UE) n° 1143/2014][e1] du 22 oct. 2014         | General framework for invasive alien species prevention and management. Surveillance, rapid eradication, management obligations.                |
| [Règlement d'exécution (UE) 2016/1141][e2] du 13 juill. 2016 | Initial EEE list — includes _Vespa velutina nigrithorax_ (the only insect on the list).                                                       |
| Updates 2017, 2019, **2022** (3rd update entered into force 2 Aug 2022) | 88 species total post-2022; _V. velutina_ remains listed.                                                                            |

[e1]: https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=celex:32014R1143
[e2]: https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32016R1141

### What aristech (automated apiary deterrent) is allowed to do

**Permitted (clear legal ground):**

- Deploy **non-lethal deterrents** (visual, acoustic, water mist, mechanical disturbance) at one's own apiary — no specific regulation; falls under normal property / _cheptel_ management (Code rural L211-1).
- Deploy **selective traps** (geometry excluding _A. mellifera_ and most pollinators — funnel, Japanese, Néoppi types) — explicitly endorsed by the 2025 law/decree language on "piégeage sélectif".
- Destroy a _V. velutina_ worker that enters the rucher (EEE-listed; killing them is the policy objective).
- Report nests via the _maire_ (Art. L411-9-1, II nouveau).

**Forbidden / restricted:**

- Killing or capturing any **protected insect** (Arrêté 23 avril 2007). Sanctioned by **Art. L415-3 Code env.** — up to **3 years prison + 150 000 €**, **7 years + 750 000 €** en bande organisée.
- Bell- or bottle-type **non-selective traps** — not yet criminally forbidden as such, but the 2025 framework "piégeage sélectif" disfavours them. Deploying one that kills protected species exposes the operator to L415-3.
- Keeping live _V. velutina_ specimens without préfectoral authorisation (Art. L411-6 + Arrêté 14 fév. 2018).
- Releasing chemicals on bees (general phytosanitary + animal welfare law applies to the _cheptel apicole_).

**Grey areas / open questions:**

- **No specific text on automated devices.** Aristech-class systems are not named in any law as of 2026-05-19. The legal test is the _result_ (did it kill protected species? did it deploy a forbidden trap geometry?).
- Animal welfare for wild insects: **no binding text** in France protects _V. velutina_ individuals on welfare grounds — the species is on the EU list, so euthanasia is policy-aligned. Welfare rules in Code rural L214-1 concern vertebrates only.
- Spraying liquids in open air: unregulated per se, but if the liquid is a biocide / phytosanitaire, Code rural L253-1+ applies (homologation, applicateur certifié).

### Queens — legal mandate vs guidance

**Hard law: none.** No French text mandates the killing of _V. velutina_ queens (fondatrices). The 2025-237 law and 2025-1377 decree speak of "piégeage sélectif" and destruction of **nests**, not of an obligation to trap queens.

**Soft guidance (non-binding):**

- **MNHN** ([frelonasiatique.mnhn.fr][gn1]) and **ITSAP-Institut de l'abeille** ([article ITSAP][gn2]) discourage generalised spring trapping: INRAE BioSP studies (CNOPSAV apiculture experts, Dec. 2020) show > 99% bycatch of non-target insects with classic bottle traps, and questionable population-level effect.
- ITSAP / CNOPSAV position: spring trapping **only at apiaries that suffered heavy attacks the previous year**, with selective traps, under organised collective protocols.
- The 2025 framework adopts this scientific position by writing "**piégeage sélectif**" into Art. L411-9-1 — selectivity becomes a _legal_ requirement for trapping carried out within the national/departmental plan; the threshold of selectivity is delegated to the plan, still pending publication as of May 2026.

[gn1]: https://frelonasiatique.mnhn.fr/piegeage-de-printemps/
[gn2]: https://itsap.asso.fr/articles/frelon-asiatique-evaluation-de-l-efficacite-du-piegeage-de-printemps

### Penalty framework

**Nest not destroyed after reporting**: no direct criminal penalty in 2025-237. The law organises _signalement et destruction_ through the _maire_ / préfet; failure to act is administrative (the préfet can substitute under L411-7, costs recoverable). No personal fine for the property owner simply for hosting a nest.

**Non-selective trap kills a protected pollinator**:

- Art. L411-1 Code env. (destruction d'espèce protégée) violated.
- **Art. L415-3 Code env.** — up to **3 years imprisonment and 150 000 €**; **7 years + 750 000 €** en bande organisée.
- If the species is on the EU Habitats Directive Annexes, EU infringement risk also.

**Introducing, holding, transporting live _V. velutina_**: Art. L411-6 + Arrêté 14 fév. 2018 violated → L415-3 same penalties.

### Legal framework — synthesis (hard constraints for aristech)

Four constraints become **hard legal safeguards**, not just ethics:

1. **Never harm an _Apis mellifera_** — falls under _cheptel_ damage (civil) and, if the bees belong to another apiarist, criminal property damage (Code pénal).
2. **Never harm a protected wild pollinator** — _binding criminal sanction_ under L411-1 + L415-3 (3 years + 150 000 €). This is the strongest constraint and justifies a **hard guard** in the architecture: vision-based species classifier with conservative "abstain → don't act" default.
3. **Any trap-like behaviour must be sélectif** — now written into Code de l'environnement (L411-9-1, since 14 Mar 2025). The exact selectivity threshold is delegated to the _plan national_ (pending publication), so the safest engineering target is "no capture of any insect other than _V. velutina_".
4. **No release of biocides / phytosanitaires** without homologation (Code rural L253-1+). A water/air/sound deterrent stays outside this regime; any chemical does not.

**Honest gaps:**

- Légifrance pages could not be opened directly during the survey; article text was reconstructed from converging secondary sources (institutional summaries, official press releases, government portals). Re-verify L411-9-1 and L411-9-2 wording on Légifrance before publishing.
- The **plan national** itself (selectivity thresholds, allowed device categories) is **not yet published** as of 2026-05-19; the décret 2025-1377 only sets adoption procedure. Aristech's compliance target is a **moving one over 2026**.
- No text consulted establishes a general legal duty to kill queens; the question stays in the realm of scientific recommendation, now partially codified through the "piégeage sélectif" wording.

## Convergent findings across sources

1. **YOLO-family is the de-facto SOTA**. Both academic papers (VespAI,
   Kim 2023, YOLOv7-Tiny 2025) and the most active open-source repos
   (vespCV) converge on YOLOv5s / YOLOv8 / YOLOv10n fine-tuned on a
   ~2-3 k labelled Vespa velutina image corpus.
2. **The total available labelled data is small** (Hornet3000+ at ~3 k,
   Roboflow ~700+, Kim 2023 ~2 k). Heavy use of pretraining and
   augmentation is mandatory.
3. **No permissive-licence production-ready detector exists**. The path
   to a redistributable aristech detector is to reimplement around a
   permissively-licenced backbone (Apache-2.0 RT-DETR or Grounding-DINO)
   rather than vendor GPL/NC code.
4. **Acoustic detection is a real second modality**, not just a
   complement. Hall 2025 reports 98.7% on hovering sound alone, with a
   different failure mode from vision (microphones don't care about
   light or occlusion).
5. **The multimodal (vision + audio) niche is empty** in the published
   literature — an opportunity for aristech to contribute something
   genuinely new rather than re-implementing existing work.

## Open decisions (to take from this survey)

These are the choices that the survey informs but does not resolve.
Each will be logged in `PROJECT_LOG.md` with rationale once decided.

1. **Detector backbone**: YOLOv8s/v10n (community, edge support, but
   AGPL/GPL) vs. RT-DETR (permissive Apache-2.0, less mature insect
   fine-tunes) vs. Grounding-DINO (zero-shot, useful for bootstrapping
   labels). Trade-off: maturity / license / inference cost.
2. **Dataset strategy**: build a merged corpus from BeeAlarmed +
   Hornet3000+ + Roboflow "Asian Hornet Detection" + own apiary footage,
   or pursue a partnership with INRAE/MNHN for higher-quality French data.
3. **Audio modality**: ship audio-first (cheaper, omnidirectional, but
   no localisation), vision-first (species + bbox), or both with audio
   as wake-up signal for the vision pipeline.
4. **Deterrent decision** (was `neutralize-target-deferred`): non-lethal
   water-jet direction validated. The auto-aim turret survey above
   confirms feasibility (Photonic Fence prior art) but no public
   project combines insect-class vision discrimination with a water
   jet — that's the niche. Final lethality / fail-safe / multimodal-
   confirm policy to be locked in a dedicated PR that amends
   `docs/architecture.md` and `PROJECT_LOG.md`.

## Caveats on this survey

- During the survey, several GitHub repo pages and academic preprint
  pages refused direct WebFetch — stars, last-commit dates, exact
  licence text and reported metrics should be **re-verified manually**
  before being used to justify a hard project decision.
- The survey is **a snapshot dated 2026-05-19**; this area moves fast
  (multiple V. velutina YOLO papers landed in 2024-2025). Re-run before
  any major architectural commitment.
- Anything in this document that says "no code surfaced" means _no
  publicly accessible code was found during this pass_ — not necessarily
  that the authors never published one. Direct correspondence with
  authors may unlock material.
