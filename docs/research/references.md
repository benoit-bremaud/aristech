# References — aristech research

Centralised bibliography of every source cited during the
state-of-the-art survey ([state-of-the-art.md](state-of-the-art.md)).
Grouped by domain. Every entry has at least a title and a direct URL;
the columns vary per section to match the nature of the source
(datasets carry size and license, papers carry year and venue, laws
carry promulgation date and status, etc.). Add new sources here as the
project progresses — this is the single index to come back to.

## Conventions

- **Survey date**: 2026-05-19. All URLs were reachable on that date
  (a few via secondary mirrors when WebFetch refused the canonical
  page). Re-verify links annually for rot.
- **Relevance** (when shown): _high / medium / low_ for aristech
  specifically, not for the field at large.
- **License / status** (when shown): only the value strictly
  observed on the source page is reported; "undeclared" means no
  SPDX or visible licence file at the time of survey.
- **Section columns are not uniform.** A reference to a law has
  different fields than a reference to a GitHub repository. The
  schema below documents what each section's columns mean.

### Per-section column schemas

| Section                            | Columns used                                              |
| ---------------------------------- | --------------------------------------------------------- |
| 1. Kaggle                          | Type, Source, Year, Relevance, Notes                       |
| 2. Vespa velutina repos            | Type, Source, Year, License, Relevance, Notes              |
| 3. Adjacent repos                  | Source, Notes                                              |
| 4. FR / EU organisations           | Source, Notes                                              |
| 5. Vision papers                   | Source, Year, Venue, Relevance                             |
| 6. Acoustic / multimodal papers    | Source, Year, Venue, Relevance                             |
| 7. HuggingFace models              | Source, Architecture, Notes                                |
| 8. Pretrained backbones            | Source, License, Notes                                     |
| 9.1 Civilian turrets               | Source, License, Notes                                     |
| 9.2 Animal deterrent fluid path    | Source, Notes                                              |
| 9.3 Insect-specific aim            | Source, Notes                                              |
| 9.4 Tracking algorithms            | Source, License, Notes                                     |
| 9.5 Ballistic / water-jet aiming   | Source, Notes                                              |
| 10. Legal — France                 | Source, Date, Relevance                                    |
| 11. Legal — EU                     | Source, Effect                                             |
| 12. Government / institutional     | Source, Notes                                              |

---

## 1. Vespa velutina detection — datasets and competitions (Kaggle)

| Type     | Source                                                                                                       | Year | Relevance | Notes                                                       |
| -------- | ------------------------------------------------------------------------------------------------------------ | ---- | --------- | ----------------------------------------------------------- |
| Dataset  | [Hornet3000+ (Marco Ry van Dijk)](https://www.kaggle.com/datasets/marcoryvandijk/vespa-velutina-v-crabro-vespulina-vulgaris) | n/a  | high      | Only V. velutina-specific Kaggle dataset. ~3000+ images, object detection labels. |
| Dataset  | [European wasp Vespula vulgaris (KITTI)](https://www.kaggle.com/tegwyntwmffat/european-wasp-vespula-vulgaris-kitti-format) | n/a  | low       | Wrong species (V. vulgaris).                                |
| Dataset  | [BeeImage Dataset](https://www.kaggle.com/datasets/jenny18/honey-bee-annotated-images)                       | n/a  | medium    | A. mellifera only. Useful as negative-class supplement.     |
| Notebook | [2022 UC Asian Hornet Detection — YOLOv5](https://www.kaggle.com/code/lucaordronneau/2022-uc-asianhornetdetection-yolov5) | 2022 | medium    | YOLOv5 on Hornet3000+.                                      |
| Notebook | [Asian Hornet Detection — Swin Transformer / MMDet](https://www.kaggle.com/code/johanmoncouti/asian-hornet-detection-swin-transformer-mmdet) | 2022 | medium    | Swin-T on Hornet3000+.                                      |
| Competition | [iNaturalist FGVC 2021](https://www.kaggle.com/c/inaturalist-2021)                                       | 2021 | low       | Generic species recognition, not V. velutina.               |

## 2. Vespa velutina detection — code repositories (GitHub)

| Type    | Source                                                                                                               | Year         | License            | Relevance | Notes                                                                 |
| ------- | -------------------------------------------------------------------------------------------------------------------- | ------------ | ------------------ | --------- | --------------------------------------------------------------------- |
| Repo    | [andrw3000/vespai (VespAI, Univ. Exeter)](https://github.com/andrw3000/vespai)                                       | 2024         | **CC BY-NC-SA 4.0** | high (ref) | Reference implementation of VespAI (Nature Comms Biology). NC license blocks commercial use. |
| Repo    | [vespCV/vespcv](https://github.com/vespCV/vespcv)                                                                    | active 2024-25 | **GPL-3.0**        | high (ref) | Ultralytics YOLOv11s on Raspberry Pi 4. Viral license.                |
| Repo    | [vespCV/hornet3000](https://github.com/vespCV/hornet3000)                                                            | 2025-01      | GPL-3.0            | medium    | YOLOv10n training tutorial on Pi 4 + Arducam.                          |
| Repo    | [vespCV/gv2-esp32](https://github.com/vespCV/gv2-esp32)                                                              | n/a          | undeclared         | medium    | ESP32-S3 + Grove Vision AI V2; explicitly designed to drive a deterrent.|
| Repo    | [lbrejon/Localization-of-Asian-hornets-with-CNN-using-CAM](https://github.com/lbrejon/Localization-of-Asian-hornets-with-CNN-using-CAM) | n/a          | undeclared         | low       | Student-style ResNet18 + CAM.                                          |
| Repo    | [Jodaille/Jobee](https://github.com/Jodaille/Jobee)                                                                  | n/a          | undeclared         | low       | OpenCV heuristic colour detection. Baseline only.                      |
| Repo    | [Barrois/Detecteur-ESP32-Cam-Blob-Detector](https://github.com/Barrois/Detecteur-ESP32-Cam-Blob-Detector)            | n/a          | undeclared         | low       | C++ ESP32-CAM acoustic-trigger + blob.                                 |

## 3. Adjacent code (apiary IoT, bee tracking, insect detection)

| Source                                                              | Notes                                                                         |
| ------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| [BeeAlarmed/BeeAlarmed](https://github.com/BeeAlarmed/BeeAlarmed)    | TF + OpenCV. Multi-class bee / wasp / pollen / varroa. **Best transfer-learning starting point**. |
| [BeeAlarmed/BeeDataset](https://github.com/BeeAlarmed/BeeDataset)    | TFDS published multi-label bee dataset.                                       |
| [Mjrovai/Bee-Counting](https://github.com/Mjrovai/Bee-Counting)      | YOLOv8 → NCNN on Raspberry Pi Zero 2W. Edge-deployment template.              |
| [matpalm/bnn](https://github.com/matpalm/bnn)                        | U-Net bee position bitmap on Pi + Intel NCS / JeVois.                          |
| [t9s9/BeeMeter](https://github.com/t9s9/BeeMeter)                    | CNN detection + multi-frame tracking + counting zone.                          |
| [Gratheon/models-gate-tracker](https://github.com/Gratheon/models-gate-tracker) | Maintained fork of BeeAlarmed for hive-entrance tracking.                  |
| [Honey-Pi org](https://github.com/Honey-Pi)                          | Pi-based hive telemetry (non-vision IoT side).                                  |
| [avsthiago/deepbee-source (DeepBee)](https://github.com/avsthiago/deepbee-source) | Comb-image analysis. Mature codebase, different problem.                       |

## 4. French and EU organisations / datasets / projects

| Source                                                                                | Notes                                                                                    |
| ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| [MNHN — Frelon Asiatique (INPN)](https://frelonasiatique.mnhn.fr/)                    | National citizen-science reporting portal. Canonical sighting database. No code.         |
| [INPN Espèces (MNHN)](https://inpn.mnhn.fr/espece/cd_nom/433589)                      | Species observation app from MNHN.                                                       |
| [SignalNids](https://signalnids.fr/)                                                  | Web app to declare nests + view the map. Community-run.                                   |
| [INRAE](https://www.inrae.fr/)                                                        | Original radio-tag tracking research. Agiir reporting app. No open detection code.       |
| [LOCNEST (KissKissBankBank)](https://www.kisskissbankbank.com/en/projects/locnest-une-solution-libre-pour-localiser-les-nids-de-frelons-asiatiques) | **Open-source 3D-printable hornet-tracking hardware**. Directly relevant to aristech.   |
| [Roboflow Universe — Asian Hornet Detection](https://universe.roboflow.com/use-case-asian-hornet-detection/asian-hornet-detection-a6ael) | ~711+ labelled images, reusable for fine-tuning. Overlaps Hornet3000+.                  |
| [Roboflow Universe — vespa-velutina](https://universe.roboflow.com/vespa-velutina-iatlu/vespa-velutina-vz4fd) | Additional V. velutina labelled corpus.                                                 |
| [ITSAP — Institut technique et scientifique de l'abeille et de la pollinisation](https://itsap.asso.fr/) | French technical reference institute. Position paper on spring trapping (see below).    |
| [ITSAP — efficacité du piégeage de printemps](https://itsap.asso.fr/articles/frelon-asiatique-evaluation-de-l-efficacite-du-piegeage-de-printemps) | Why spring trapping is discouraged: >99% bycatch, questionable population effect.        |

## 5. Academic papers — vision-based detection

| Source                                                                                                                | Year | Venue                                  | Relevance |
| --------------------------------------------------------------------------------------------------------------------- | ---- | -------------------------------------- | --------- |
| [VespAI: a deep learning-based system for the detection of invasive hornets](https://www.nature.com/articles/s42003-024-05979-z) | 2024 | Nature Communications Biology          | **high** — current SOTA reference. |
| [VespAI on PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10991484/)                                                   | 2024 | Open-access mirror                     | high      |
| [Deep Learning-Based Portable Image Analysis System for Real-Time Detection of Vespa velutina (Kim et al.)](https://www.mdpi.com/2076-3417/13/13/7414) | 2023 | MDPI Applied Sciences 13(13):7414      | high      |
| [Improving Hornet Detection with the YOLOv7-Tiny Model](https://www.techscience.com/cmc/v83n2/60597/html)             | 2025 | Computers, Materials & Continua        | medium    |
| [Détection… des attaques de frelon asiatique… par deep learning et vidéosurveillance (HAL-INRAE)](https://hal.inrae.fr/hal-03258615) | 2021 | Conf. IA & Biodiversité                | medium    |
| [Method for Nest Detection of the Yellow-Legged Hornet in High Density Areas](https://pmc.ncbi.nlm.nih.gov/articles/PMC10926382/) | 2024 | Insects / MDPI                         | low (nest, not individual hornets) |

## 6. Academic papers — acoustic and multimodal detection

| Source                                                                                                            | Year | Venue                                   | Relevance |
| ----------------------------------------------------------------------------------------------------------------- | ---- | --------------------------------------- | --------- |
| [Remote and automated detection of Asian hornets… (Hall et al.)](https://www.sciencedirect.com/science/article/pii/S0168169925004132) | 2025 | Computers and Electronics in Agriculture 235 | **high** — 98.7% acoustic accuracy. |
| [Hall et al. — NTU IRep](https://irep.ntu.ac.uk/id/eprint/53340/)                                                 | 2025 | Open-access mirror                      | high      |
| [Automated detection of the yellow-legged hornet using an optical sensor with machine learning (Herrera et al.)](https://scijournals.onlinelibrary.wiley.com/doi/full/10.1002/ps.7296) | 2023 | Pest Management Science                 | medium (proprietary sensor)        |

## 7. HuggingFace models

| Source                                                                | Architecture                          | Notes                                                                   |
| --------------------------------------------------------------------- | ------------------------------------- | ----------------------------------------------------------------------- |
| [Honey-Bee-Society/honeybee_ml_v1](https://huggingface.co/Honey-Bee-Society/honeybee_ml_v1) | AutoGluon MultiModalPredictor    | Coarse Vespidae class only.                                              |
| [MuGeminorum/insecta](https://huggingface.co/MuGeminorum/insecta)     | Object detection over 2 037 insect taxa | Verify license + species coverage before relying.                       |
| [mnauf/detect-bees (Space)](https://huggingface.co/spaces/mnauf/detect-bees) | YOLO-family demo                      | Demo, not deployable model.                                              |

## 8. Pretrained backbones — candidates for fine-tuning

| Source                                                                                              | License       | Notes                                                                                    |
| --------------------------------------------------------------------------------------------------- | ------------- | ---------------------------------------------------------------------------------------- |
| [Ultralytics YOLOv8](https://docs.ultralytics.com)                                                  | **AGPL-3.0**  | Strong small-object, mature exports. Licence has commercial implications.                 |
| [YOLOv10 (THU-MIG)](https://github.com/THU-MIG/yolov10)                                             | AGPL-3.0      | NMS-free head. Already proven on Pi for V. velutina (vespCV).                            |
| [YOLOv9 (WongKinYiu)](https://github.com/WongKinYiu/yolov9)                                         | GPL-3.0       | Best mAP/latency at small-object scales.                                                  |
| [RT-DETR / RF-DETR](https://huggingface.co/PekingU/rtdetr_r50vd)                                    | **Apache-2.0**| Transformer, NMS-free, strong on cluttered scenes. **Most aristech-compatible license.**  |
| [Grounding-DINO (IDEA-Research)](https://huggingface.co/IDEA-Research/grounding-dino-tiny)          | Apache-2.0    | Open-vocabulary. Zero-shot pre-labelling pipeline.                                        |
| [YOLO-World](https://huggingface.co/spaces/stevengrove/YOLO-World)                                  | GPL-3.0       | Real-time open-vocabulary YOLOv8-based.                                                   |

## 9. Auto-aim turret prior art

### 9.1 Civilian / DIY turrets (mostly human-sized targets)

| Source                                                                                          | License            | Notes                                                  |
| ----------------------------------------------------------------------------------------------- | ------------------ | ------------------------------------------------------ |
| [Project Sentry Gun (Rudolph Labs)](https://github.com/sentryGun53/Project-Sentry-Gun)          | OSS, no SPDX       | Canonical sentry turret reference. Legacy.             |
| [HackerShack Tracking-Turret](https://github.com/HackerShackOfficial/Tracking-Turret)           | Unlicensed         | Pi + OpenCV + Nerf flywheel.                            |
| [anjrew/Autonomous-Nerf-Turret](https://github.com/anjrew/Autonomous-Nerf-Turret)               | **MIT**            | YOLO + centroid PID. **Most reusable license.**         |
| [dhairyamishra/NERF_OPENCV_turret](https://github.com/dhairyamishra/NERF_OPENCV_turret)          | undeclared         | Trapezoidal motion profile, FastAPI control.            |
| [KevyVo/3D-Printed-AI-Nerf-Sentry-Turret](https://github.com/KevyVo/3D-Printed-AI-Nerf-Sentry-Turret) | undeclared        | 3D-printed chassis.                                     |
| [rjean/tracker](https://github.com/rjean/tracker)                                               | undeclared         | Coral Edge TPU + MobileNet-SSD.                          |
| [chenalan02/LaserPointerMotionDetection](https://github.com/chenalan02/LaserPointerMotionDetection) | undeclared       | OpenCV bg-sub + 5 mW laser.                              |
| [PaintCam Eve (OZ-IT)](https://www.paintcam.net/)                                               | proprietary        | Closed-source commercial product.                        |

### 9.2 Animal deterrent — mechanical fluid path

| Source                                                                                                                              | Notes                                                                |
| ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| [Orbit Yard Enforcer 62100](https://www.orbitonline.com/products/yard-enforcer-motion-activated-sprinkler)                          | Hose-fed PIR sprinkler. 10-21 m range. Reference fluid path.          |
| [Bird-X Hydro Critter Blaster](https://bird-x.com/bird-products/hydro-critter-blaster/)                                             | Solar-powered version of the above.                                   |
| [DIY 12V diaphragm pump kits (BD-07W class)](https://bodenpump.com/product/bd-07w-12v-24v-mini-diaphragm-water-pumps-water-purifier-pump-brush/) | Pump + solenoid + nozzle. 12V, 4.5 L/min, 110 PSI. Standard DIY recipe. |

### 9.3 Insect-specific aim (the closest prior art)

| Source                                                                                                              | Notes                                                                              |
| ------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| [Photonic Fence (Nature Sci. Reports 2020)](https://www.nature.com/articles/s41598-020-71824-y)                     | **Only published proof** that an insect can be hit by a steerable beam at metre-scale with 25 ms pulse and <2 px error. Galvanometers, not servos. Patent-encumbered. |
| [Ildaron/Laser_control](https://github.com/Ildaron/Laser_control)                                                   | Jetson Nano + YOLOv4-tiny + galvanometer mirrors. 24-35 FPS on mosquitoes.          |
| [mcoates12/autonomous-mosquito-turret](https://github.com/mcoates12/autonomous-mosquito-turret)                     | Stereo + servo prototype.                                                          |
| [Nassif101/Mosquito-Laser-Defence-Turret](https://github.com/Nassif101/Mosquito-Laser-Defence-Turret)               | Embedded real-time vision-guided laser.                                            |

### 9.4 Tracking algorithms

| Source                                                            | License       | Notes                                                |
| ----------------------------------------------------------------- | ------------- | ---------------------------------------------------- |
| [OpenCV legacy trackers (MOSSE, KCF, CSRT)](https://learnopencv.com/object-tracking-using-opencv-cpp-python/) | BSD           | Built-in `cv2.legacy.Tracker*_create`.               |
| [FoundationVision/ByteTrack](https://github.com/FoundationVision/ByteTrack) | MIT           | Multi-object tracker. Associates low-conf boxes.     |
| [noahcao/OC_SORT](https://github.com/noahcao/OC_SORT)             | MIT           | Robust to occlusion and non-linear motion.            |
| [Roboflow `trackers`](https://github.com/roboflow/trackers)        | Apache-2.0    | SORT / ByteTrack / OC-SORT / BoT-SORT in one API.   |

### 9.5 Ballistic / water-jet aiming

| Source                                                                                                                  | Notes                                                                  |
| ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| [Hu et al., Two-Stage Water Jet Landing Point Prediction (Sensors 2021)](https://www.mdpi.com/1424-8220/21/8/2704/htm)  | CV-based landing-point regression for firefighting robots.             |
| [Improved Near-Field CV for Jet Trajectory (Sensors 2020)](https://www.mdpi.com/1424-8220/20/24/7029)                   | Particle-kinematics ballistic + image closed-loop correction.           |
| [UAV-imagery Jet Trajectory Detection (Sensors 2024)](https://www.mdpi.com/1424-8220/24/11/3553)                        | Learnable prompts to segment jet stream.                                |
| [Water Jet Trajectory Model of Fire Monitor (2018)](https://www.researchgate.net/publication/329571016)                 | Closed-form parabolic + drag equations.                                 |
| [Self-Choreographed Musical Fountain System](https://www.researchgate.net/publication/312276164)                        | Pi + Arduino + PCA9685 valve drivers — fluid plumbing reference.        |

### 9.6 Deterrent media beyond pure water (projectile / impact)

| Source                                                                                                                              | Notes                                                                                          |
| ----------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| [Fabian et al., proportional-navigation interception (PMC 2018)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6228472/)             | Hitting an agile flying target needs closed-loop guidance — argues against single-shot projectiles. |
| [Air vortex cannon (Wikipedia)](https://en.wikipedia.org/wiki/Air_vortex_cannon)                                                    | Zero-medium momentum "punch", ~12 m range. Candidate zero-trace impact arm.                     |
| [Vortex ring gun (Wikipedia)](https://en.wikipedia.org/wiki/Vortex_ring_gun)                                                        | Crowd-control variant abandoned 1998: unpredictable vortices + limited range (short-range only). |
| [Are paintballs biodegradable? (Punisher PB)](https://punisherspb.com/blogs/news/are-paintballs-biodegradable)                      | Gelatin shell + PEG fill, food-grade, degrades in weeks–months. Real biodegradable projectile.  |
| [Paintballs are environmentally safe (Paintball USA)](https://www.paintballusa.org/blog/paintballs-are-environmentally-safe)        | Corroborates composition + water-soluble degradation.                                           |
| [Environmental impact of Orbeez (greenmatch)](https://www.greenmatch.co.uk/blog/environmental-impact-of-orbeez)                     | Sodium-polyacrylate water beads = not biodegradable; microplastic concern.                      |
| [Sodium polyacrylate is non-degradable (microplasticsolution)](https://www.microplasticsolution.com/post/ever-heard-of-sodium-polyacrylate-the-non-degradable-superabsorbent-synthetic-polymer) | Persistent superabsorbent acrylic.                                       |
| [Sodium polyacrylate (Wikipedia)](https://en.wikipedia.org/wiki/Sodium_polyacrylate)                                                | Composition / non-biodegradability reference.                                                   |
| [Biodegradability of bio-based vs synthetic hydrogels (Wiley, app.53655)](https://onlinelibrary.wiley.com/doi/10.1002/app.53655)    | Alginate hydrogels biodegrade in soil; review of soil-amendment hydrogels.                      |
| [Swelling/degradation of Ca²⁺/Ba²⁺ alginate beads (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S1381514804000161) | Ca-alginate swells ~160 % then dissolves; only Ba²⁺ stabilises (toxic).            |
| [Starch-derived superabsorbents in agriculture (Springer)](https://link.springer.com/article/10.1007/s00289-021-03842-3)           | Starch SAP biodegradable, non-toxic, ~400× water uptake.                                        |
| [Starch-based superabsorbent for shrubs (MDPI Agriculture)](https://www.mdpi.com/2077-0472/13/10/1893)                              | Field-application evidence for starch SAP.                                                       |

## 10. Legal framework — France

| Source                                                                                  | Date         | Relevance |
| --------------------------------------------------------------------------------------- | ------------ | --------- |
| [Arrêté du 26 décembre 2012 — Légifrance](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000026844543) | 26 Dec 2012  | high      |
| [LOI 2016-1087 du 8 août 2016 — Légifrance](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000033016237) | 8 Aug 2016   | high      |
| [Arrêté du 14 février 2018 — Légifrance](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000036629851) | 14 Feb 2018  | high      |
| [Arrêté du 2 mars 2023 — Légifrance](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000047411674) | 2 Mar 2023   | medium    |
| [Arrêté du 23 avril 2007 — insectes protégés](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000465500) | 23 Apr 2007  | **critical** — basis for L415-3 penalty (3 years + 150 000 €). |
| [Code rural et de la pêche maritime](https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006071367/) — Art. L211-1, L211-6/7 | consolidated | medium — honey bees as _cheptel_, mandatory declaration, préfectoral distance rules. |
| **[LOI n° 2025-237 du 14 mars 2025 — Légifrance](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000051329052)** | **14 Mar 2025** | **critical** — current law on V. velutina proliferation. The one the user remembered. |
| **[Décret n° 2025-1377 du 29 décembre 2025 — Légifrance](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000053201550)** | 29 Dec 2025  | high      |
| [Article L411-9-1 — Légifrance](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000051331438) | active       | high      |
| [Code env. — Sous-section EEE L411-5 à L411-7](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006074220/LEGISCTA000033031225/) | active       | high      |
| [Code env. — Section sanctions L415-3 à L415-8](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006074220/LEGISCTA000006176527/) | active       | **critical** |

## 11. Legal framework — EU

| Source                                                                                  | Effect                                                          |
| --------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| [Règlement (UE) 1143/2014 — EUR-Lex](https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=celex:32014R1143) | Framework for invasive alien species.                            |
| [Règlement d'exécution (UE) 2016/1141 — EUR-Lex](https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32016R1141) | Initial EEE list. V. velutina included (only insect on list).   |

## 12. Government and institutional pages

| Source                                                                                                                                    | Notes                                                                                |
| ----------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| [Agriculture.gouv.fr — Frelon asiatique réglementation](https://agriculture.gouv.fr/le-frelon-asiatique-quelle-reglementation)            | Synthesis page from the Ministry of Agriculture.                                       |
| [Banque des Territoires — procédure d'adoption des plans](https://www.banquedesterritoires.fr/lutte-contre-la-proliferation-du-frelon-asiatique-la-procedure-dadoption-des-plans-daction-est) | Analysis of the 2025-1377 decree application procedure.                              |
| [GDS France — analyse de la loi 2025-237](https://www.gdsfrance.org/la-nouvelle-loi-sur-le-frelon-asiatique-un-cadre-renforce-pour-une-lutte-efficace/) | Reading of the 14 Mar 2025 law by Groupements de Défense Sanitaire France.            |
| [MNHN — piégeage de printemps](https://frelonasiatique.mnhn.fr/piegeage-de-printemps/)                                                    | MNHN scientific position on spring trapping (discouraged in general use).             |

## 13. Behavioural biology — V. velutina at the hive entrance

Sources surfaced in [prototype-foundations.md § A](prototype-foundations.md).

| Source                                                                                                                                | Year      | Relevance | Notes                                                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------- | --------- | --------- | ------------------------------------------------------------------------------------------------------ |
| [Tan et al., Bee-hawking by V. velutina, _Naturwissenschaften_](https://link.springer.com/article/10.1007/s00114-006-0210-2)         | 2007      | high      | Hunting technique; > 25 min hover bouts; A. mellifera 3× more vulnerable than A. cerana.               |
| [Monceau et al., Native Prey vs Invasive Predator, _PLOS ONE_](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0066492) | 2013   | high      | Field study at French apiaries.                                                                        |
| [Monceau et al., Predation pressure dynamics, _Apidologie_](https://link.springer.com/article/10.1007/s13592-012-0172-7)              | 2013      | medium    | Wind/rain suppress hunting; seasonal peak Aug-Oct.                                                     |
| [Monceau et al., _V. velutina_: a new invasive predator, _J. Pest Sci._](https://link.springer.com/article/10.1007/s10340-013-0537-3) | 2014      | medium    | Population-scale review.                                                                               |
| [Poidatz et al., RFID activity rhythm, _Ecology & Evolution_](https://pmc.ncbi.nlm.nih.gov/articles/PMC6106190/)                       | 2018      | **high**  | Diel pattern 07:00-20:00, peak 14:00-15:00; foraging range ~1 km.                                       |
| [Sauvard et al., Flight capacities, _PLOS ONE_](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0198597)            | 2018      | **high**  | Ground speed 6.66 ± 2.31 m/s unladen, 4.06 ± 1.34 m/s laden.                                            |
| [Rojas-Nossa et al., Long-term predation pressure, _Apidologie_](https://link.springer.com/article/10.1007/s13592-025-01158-z)        | 2025      | high      | Temperature 15-26 °C, RH > 60 %; diel shift Jul-Aug vs Sep-Oct.                                         |
| [Arca et al., Defensive behaviour of A. mellifera, _Behav. Processes_](https://www.sciencedirect.com/science/article/abs/pii/S0376635714001223) | 2014 | high      | A. m. mellifera lacks heat-balling; A. cerana defends.                                                  |
| [Ken et al., Heat-balling, _Naturwissenschaften_](https://link.springer.com/article/10.1007/s00114-005-0026-5)                         | 2005      | medium    | A. cerana 46 °C in 3 min; lethal limit 45.7 °C for hornet.                                              |
| [Requier et al., Foraging paralysis, _Ecol. Appl._](https://www.researchgate.net/publication/329111215)                                | 2019      | **high**  | A. mellifera clusters and stops flying under hornet pressure.                                            |
| [Cheng et al., Sting venom as alarm pheromone, _J. Exp. Biol._](https://journals.biologists.com/jeb/article/220/4/645/18673/)         | 2017      | high      | A missed strike triggers cascading hornet recruitment.                                                  |
| [Cheng et al., Defensive behaviour vs stimuli, _Insects_](https://pmc.ncbi.nlm.nih.gov/articles/PMC8034368/)                          | 2021      | low       | Auditory/colour/hair stimuli trigger aggression but no documented deterrent effect.                     |
| [Rojas-Nossa et al., Electric harps, _Pest Manag. Sci._](https://pmc.ncbi.nlm.nih.gov/articles/PMC9825959/)                            | 2022      | **high**  | **−89 %** predation pressure at apiary scale — the deterrent benchmark to beat.                         |
| [Rome et al., Predatory habits in France, MNHN/HAL](https://mnhn.hal.science/hal-03180854v1)                                          | 2021      | high      | Diet 38.1 % bees, 29.9 % flies, 19.7 % wasps.                                                          |
| [Rome, Muller, Villemant — MNHN identification sheet](https://sitesv2.anses.fr/en/system/files/private/Vespa%20velutina%20Identification%20Sheet%20MNHN_2.pdf) | undated | medium | Body length, colour markings — visual ID reference.                                                     |

## 14. Éric Darrouzet body of work (IRBI / Université de Tours)

Detailed synthesis in [prototype-foundations.md § A.bis](prototype-foundations.md).

| Source                                                                                                                                                                      | Year | Type            | Relevance |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- | --------------- | --------- |
| [IRBI lab — staff page](https://www.univ-tours.fr/annuaire/m-eric-darrouzet)                                                                                                | —    | profile          | reference |
| [FRELON project site](http://frelonasiatique.univ-tours.fr/)                                                                                                                | —    | lab page         | reference |
| [IRBI publications index](http://frelonasiatique.univ-tours.fr/publications.html)                                                                                           | —    | meta             | reference |
| [Robinet/Suppo/Darrouzet — Rapid spread in France, _J. Appl. Ecol._](https://besjournals.onlinelibrary.wiley.com/doi/10.1111/1365-2664.12724)                                | 2017 | paper           | high      |
| [Kennedy/Darrouzet — Radio-telemetry nest finding, _Comms Biology_](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6123801/)                                                  | 2018 | paper           | high      |
| [Ruiz-Cristi/Berville/Darrouzet — Thermal tolerance, _PLOS ONE_](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0239742)                                 | 2020 | paper           | medium    |
| [Cheng/Wen/Tan/Darrouzet — Sex pheromone blend, _Entomologia Generalis_ (HAL)](https://hal.science/hal-03562571/)                                                            | 2022 | paper           | medium    |
| **[Thiéry & Darrouzet et al. — Electric harps, _Entomologia Generalis_](https://www.schweizerbart.de/papers/entomologia/detail/43/103168/)**                                | 2023 | paper           | **critical** — > 90 % target, < 2 % bycatch published benchmark. |
| **[Predation success at hives, _Sci. Reports_](https://pmc.ncbi.nlm.nih.gov/articles/PMC10049882/)**                                                                        | 2023 | paper           | **critical** — 2.4 % strike success, peak at ~8 simultaneous hornets. |
| [Rojas-Nossa/Darrouzet et al. — Baited trap selectiveness, _Animals_](https://pmc.ncbi.nlm.nih.gov/articles/PMC10778013/)                                                   | 2024 | paper           | high      |
| _Le frelon asiatique, un redoutable prédateur — 2nd ed._                                                                                                                    | 2023 | book (160 pp)  | high — apiarist-facing reference. Éditions SNApiculture. |
| [The Conversation FR — "Le frelon asiatique, ce dérangeant prédateur"](https://theconversation.com/le-frelon-asiatique-ce-derangeant-predateur-147676)                       | 2020 | popular         | medium    |
| [UNAF webinar — "Frelon asiatique : impacts et luttes"](https://www.youtube.com/watch?v=fDAD1jNnwfA)                                                                       | 2024 | conference talk | high      |
| [CNRS INEE — Pheromones contre le frelon](https://www.inee.cnrs.fr/fr/cnrsinfo/les-pheromones-une-solution-de-lutte-contre-le-frelon-asiatique)                              | 2022 | press           | medium    |

## 15. Hive geometry and apiary mounting

Sources surfaced in [prototype-foundations.md § B](prototype-foundations.md).

| Source                                                                                                              | Type      | Notes                                                          |
| ------------------------------------------------------------------------------------------------------------------- | --------- | -------------------------------------------------------------- |
| [Icko Apiculture — Ruche Dadant 10 cadres](https://www.icko-apiculture.com/ruche/ruches-completes/ruche-dadant-10-cadres.html) | supplier  | Standard FR Dadant 10 dimensions.                              |
| [ApiaRobotics — Dimensions et comparaison](https://apiarobotics.com/fr/connaissances/dimensions-et-comparaison-des-ruches) | reference | Cross-table of Dadant / Langstroth / Warré / Voirnot / Layens. |
| [Apiculture.net — Bien organiser votre rucher](https://www.apiculture.net/blog/bien-organiser-rucher-n12)           | reference | Stand height, orientation, spacing.                            |
| [Label Abeille — Installer ses ruches](https://label-abeille.org/fr/blog/132-ou-installer-ses-ruches-comment-organiser-le-rucher-) | reference | French installation conventions.                               |
| [Adafruit — Raspberry Pi HQ Camera lenses](https://learn.adafruit.com/raspberry-pi-hq-camera-lenses?view=all)        | tutorial  | Lens / focal-length matrix.                                    |
| [Arducam — Pi Camera v3 closer look](https://blog.arducam.com/official-camera-module-3-a-closer-look/)              | reference | IMX708 specs.                                                  |
| [Hackaday — Weatherproof Pi camera enclosure](https://hackaday.com/2023/01/18/weatherproof-raspberry-pi-camera-enclosure-in-a-pinch/) | tutorial | Outdoor mounting tips.                                         |
| [Sixfab IP65 outdoor enclosure](https://sixfab.com/product/raspberry-pi-ip65-outdoor-iot-project-enclosure/)        | product   | Commercial enclosure benchmark.                                |

## 16. Hardware BOM — compute, mechanics, fluid, power

Sources surfaced in [prototype-foundations.md § C](prototype-foundations.md). EUR prices anchored at survey date (2026-05-19); re-quote at procurement time.

### Compute and accelerators

| Source                                                                                                                                 | Notes                                |
| -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| [Raspberry Pi AI HAT+ (Hailo-8L)](https://www.raspberrypi.com/products/ai-hat/)                                                       | 13 TOPS NPU, official HAT+.          |
| [NVIDIA Jetson Orin Nano Super Dev Kit](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/) | Higher FPS but 2× the power draw.   |
| [Antratek EU — Jetson Orin Nano Super](https://www.antratek.com/nvidia-jetson-orin-nano-super-developer-kit)                          | EU reseller.                         |
| [Coral USB Accelerator](https://www.coral.ai/products/accelerator)                                                                    | Chronic allocation issues since 2023. |
| [Pi Hut — MG996R servo](https://thepihut.com/products/servo-motor-mg996r-high-torque-metal-gear)                                       | v1 servo pick.                       |
| [Gotronic — PCA9685 16-ch PWM](https://www.gotronic.fr/art-shield-i2c-pour-16-servos-ada1411-20672.htm)                               | PWM driver.                          |
| [iFlight EU — GM3506 + AS5048A](https://iflight-rc.eu/en/products/ipower-gm3506-encoder-combo-set)                                    | v2 BLDC gimbal.                      |

### Camera and optics

| Source                                                                                                                  | Notes                              |
| ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| [Raspberry Pi HQ Camera (IMX477)](https://www.raspberrypi.com/products/raspberry-pi-high-quality-camera/)                | 12.3 MP, C/CS-mount.                |
| [Kubii — Pi Camera v3](https://www.kubii.com/en/cameras-sensors/3878-camera-module-v3-raspberry-pi-3272496313699.html)  | Budget alternative with autofocus.  |
| [Arducam M12 lens docs](https://docs.arducam.com/Optics-and-Lenses/Lens-Products-from-Arducam/)                         | 6 mm wide-lens choice for aristech v1. |

### Fluid path

| Source                                                                                                                                                                                                 | Notes                                   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------- |
| [VEVOR EU — 12V diaphragm pump (BD-07W class)](https://eur.vevor.com/water-pumps-accessories-c_12381/vevor-12v-diaphragm-pump-1-8gpm-6-81-l-min-3-chamber-water-pump-pressure-switch-p_010923467134) | Reference 12V pump, 4.5 L/min @ 7 bar. |

### Audio + distance

| Source                                                                                                                                                                | Notes                                 |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| [Adafruit SPH0645 I²S MEMS mic](https://www.adafruit.com/product/3421)                                                                                                | Audio sensor pick for v1.             |
| [Botland — SPH0645 (EU)](https://botland.store/microphones-and-sound-detection/9715-sph0645lm4h-mems-i2s-microphone-adafruit-3421-5904422307103.html)                  | EU reseller.                          |
| [Pimoroni — VL53L5CX 8×8 ToF](https://shop.pimoroni.com/en-us/products/vl53l5cx-time-of-flight-tof-sensor-breakout)                                                   | Distance sensor pick for v1.          |
| [Techvers EU — Intel RealSense D435i](https://techvers.eu/en/product-2/intel-realsense-d435i-camera/?wmc-currency=EUR)                                                | v2 stereo depth option, defer.        |

### Power and solar

| Source                                                                                                                                                                                | Notes                                 |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| [WattCycle EU — 12V/100Ah LiFePO4](https://eu.wattcycle.com/products/wattcycle-12v-100ah-group-24-lifepo4-battery)                                                                     | 5-day battery autonomy.                |
| [Victron SmartSolar MPPT 75/15](https://www.victronenergy.com/solar-charge-controllers/smartsolar-mppt-75-10-75-15-100-15-100-20)                                                     | Quality MPPT.                          |
| [VEVOR EU — MPPT solar charge controllers](https://eur.vevor.com/mppt-solar-charge-controller-c_10732)                                                                                | Budget MPPT.                           |

## Maintenance

- This file is the **bibliography** ; [state-of-the-art.md](state-of-the-art.md) is the **SOTA narrative** ; [prototype-foundations.md](prototype-foundations.md) is the **applied engineering inputs**.
- New sources discovered after the initial survey (2026-05-19) should be appended in the relevant section and marked with the discovery date.
- Verify URLs annually (link rot, especially on academic preprint servers).
- Re-verify legal entries when the Plan national de lutte is published (expected 2026) — Art. L411-9-1 cross-references will change.
