# Spec — own vision model (M5)

> **Status**: Proposed (needs brainstorm 2026-10-16) · **Milestone**: M5, autumn 2027 (first
> public-data model during winter 2026–27) · **Related**: ADR-0015, ADR-0014, ADR-0001, UC8, UC9

## Need

Recognise *V. velutina* (target), *V. crabro* (non-target), the honeybee (explicit class) and other
insects in the conditions of **our** hive entrances, with a recall far above VespAI's measured
~3–13 %, under a licence that allows a product.

## Actors

- **Researcher** (primary) — annotates footage, trains and compares models.
- **Beekeeper** — benefits from better counts and alerts.

## Main scenario

1. Field recordings (spec `capture-rig`) and public data under compatible licences (CC BY, CC0;
   never NC) are inventoried with their licence.
2. The researcher annotates (UC8), with model pre-annotation corrected by hand, in a documented,
   open annotation format, with a tool chosen in the M5 ADR.
3. A **frozen test set** is split off by day and hive (no leakage).
4. A permissively licensed pre-trained detector is fine-tuned on the training split (UC9).
5. The harness (UC3) scores it per class against VespAI on the frozen set; both operating points
   (ADR-0014) are measured.
6. The model ships as a second `HornetDetector` adapter, loaded from a path.

## Captive lab (needs brainstorm Q9)

Captive *V. velutina* filmed under controlled distance, angle, light (backlight, dusk) and
background give a **robustness map** of the model (where it fails) and high-frame-rate footage of
flight. Training and robustness analysis only — never the frozen test set.

## Alternative scenarios

- **A1** Not enough field data after the season → train on public data only, label the result
  "pre-field", keep VespAI as the default detector.
- **A2** The own model does not beat VespAI on the frozen set → do not ship; analyse failure modes.
- **A3** A data source's licence is unclear → excluded until clarified.
- **A4** Captive-hornet footage (owner idea) is used for training only, never in the frozen test
  set (unnatural behaviour).

## Acceptance criteria

- **AC1** Every training image has a recorded source and licence compatible with commercial use.
- **AC2** The base model's code and weights licences are permissive (verified in the M5 ADR).
- **AC3** On the frozen set, own-model *V. velutina* recall at the COUNT point exceeds VespAI's.
- **AC4** At the ACT point, zero bees are classified as target on the frozen set.
- **AC5** The report is reproducible with one command, the dataset version and model hash recorded.
- **AC6** No training dependency enters the core `dependencies` (optional extra or separate tool).
