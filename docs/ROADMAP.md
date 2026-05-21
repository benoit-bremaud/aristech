# Aristech — Roadmap (detection-first)

The staged plan that implements [requirements.md](requirements.md). The
focus of this roadmap is the **v1 detection axis**; later tracks are
sketched and will be detailed when reached.

## Principle — an incremental staircase

Detection is not one task; it is a **staircase**. Each step is **runnable,
testable, and disposable if needed**. We only build step N+1 once step N has
passed its gate. Every gate is a **bifurcation point**: we can reorient
(model, data) without having bet everything.

Tied questions (data, evaluation, operating point) are **not single
decisions** — they progress step by step along the staircase.

## Tracking model

This document is the source of truth. When the needs are clear enough, it
will be mirrored as a GitHub **Epic + sub-issues** on Project #57: each
marche becomes an issue, its sub-tasks become sub-issues / checklist items,
its gate becomes the issue's definition of done.

## The detection staircase

### M0 — VespAI feasibility spike *(disposable)*

#### Sub-tasks

- Locate VespAI: repo, model weights, **licence**, dependencies.
- Install in an isolated environment.
- Run inference on one known hornet image; visualise the bbox.
- **Check VespAI's actual classes**: does it output "velutina"? does it
  distinguish the bee? the European hornet? (our 3-class target depends on
  this).

**🚪 Gate** — VespAI produces a correct bbox on ≥1 image, **and** licence +
deps + available classes are documented. *If unusable or wrong classes →
reconsider the model choice here, not later.*

### M1 — Batch still images + data inventory

#### Sub-tasks

- Inventory available datasets (VespAI's own dataset, GBIF, iNaturalist):
  volume, classes, **licence**.
- Run VespAI on a varied batch (velutina / bee / wasp / fly).
- Qualitative inspection: where it works, where it fails — **especially
  bee→hornet confusions** (the legal risk).

**🚪 Gate** — documented strengths/weaknesses + a list of usable data
sources with clear licences.

### M2 — Video + architecture *(first real code brick)*

#### Sub-tasks

- `VideoSource` adapter (read a video file → `VideoFrame`).
- `HornetDetector` adapter wrapping VespAI (`frame → Sequence[Detection]`),
  **mapping VespAI classes → {velutina, bee, other}**.
- Wire into `DetectHornetVisual` (CLI composition root).
- Log detections (bbox + class + confidence) + optional debug video overlay.
- Unit tests for the adapters (fakes + a small fixture).

**🚪 Gate** — `aristech` reads a clip → a stream of logged/visualisable
`Detection`; tests green; ruff/mypy clean; **runs with no hardware**.

### M3 — Evaluation harness

#### Sub-tasks

- Build an annotated test set (50–100 images/clips, 3 classes).
- Choose an annotation format + a small tool.
- Evaluation script: precision / recall / confusion matrix **per class**.
- Reproducible report (one command).

**🚪 Gate** — a per-class precision/recall figure on a **frozen** set,
recomputable on demand.

### M4 — Operating point

#### Sub-tasks

- Precision/recall vs threshold curves on the set.
- Pick the threshold such that **bee false positives = 0** (or a known
  bound).
- Implement the **abstention** policy (below threshold → no action /
  `UNKNOWN`) in the use case.
- Tests for the abstention policy.

**🚪 Gate** — documented threshold + tested abstention; "never a bee
classified as a target above threshold" **verified on the set**.

### M5 — Own data *(sketch)*

Capture protocol at the apiary → annotation pipeline → re-evaluate on **our**
conditions → optional fine-tune.

**🚪 Gate** — field evaluation ≥ public baseline; fine-tune decided or not.

### M6 — Live / embedded *(sketch)*

`Picamera2` adapter (real-time stream) → measure FPS/latency → headless
service → NPU port (Hailo).

**🚪 Gate** — stable real-time detection on the target + measured power
draw.

## Cross-cutting gate rules

- **1 marche = 1 PR** (or a few), CI green, tests, decisions logged in
  `PROJECT_LOG.md`.
- **Dependencies**: M3 needs annotations (from M1/M5); M4 needs M3; M2
  depends only on M0.
- Each gate is a **bifurcation point** — reorient without sunk cost.

## Key risk

**VespAI's classes may not match our 3 classes** (it may detect only
"hornet", with no "bee" class). The M0 check exists for this: it can turn
"wrap" into "wrap + fine-tune" earlier than planned.

## Deferred tracks (out of the detection-first scope)

- **Alert** — provisional defaults in [requirements.md](requirements.md);
  to be detailed (own staircase: local log → evidence image → remote
  notification → dashboard).
- **Acoustic axis** — feasibility (SNR at a hive), signature, role
  (wake-up trigger vs parallel confirmer).
- **After-detection** — tracking, distance, decision policy, non-lethal
  deterrence.
- **Embedded** — see M6 and the hardware target in
  [requirements.md](requirements.md).
