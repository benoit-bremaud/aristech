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
step becomes an issue, its sub-tasks become sub-issues / checklist items,
its gate becomes the issue's definition of done.

## Re-targeted plan (needs brainstorm 2026-10-16)

Own model, A0 and D0 all need field data, and hornets are active only August–November, so the
**capture rig is the critical path** ([record](architecture/reviews/needs-brainstorm-2026-10-16.md),
Q6). Order:

| When | Brick | Gate |
|---|---|---|
| Winter 2026–27 | **M3 report** — reproducible VespAI baseline on the Roboflow set (one command, committed numbers) | per-class P/R recomputable on demand |
| Winter 2026–27 | **C1 neutral collector** — fixed watchtower, camera + 2 mics on one clock, unattended recording ([spec](architecture/specs/capture-rig.md)) | a week unattended, drift ≤ 1 frame |
| Winter 2026–27 | **Annotation pipeline** + first model on public CC BY data ("pre-field") | frozen test set defined, licences recorded |
| Whenever hornets can be caught | **Captive lab** (optional) — reference wingbeat signatures (A0), robustness map (M5), enclosure deterrence pre-test (D0) | data never in the frozen test set |
| Late 2026 or Aug–Nov 2027 | **D0** field test ([spec](architecture/specs/deterrence-field-test.md)) | lasting break-off or reorient |
| Aug–Nov 2027 | **Capture season** with C1 (extend to neighbouring hives if C1 is stable) | segments collected with metadata |
| Autumn 2027 | **A0** acoustic feasibility ([spec](architecture/specs/acoustic-feasibility.md)) | role decided on data |
| Autumn 2027 | **M5 own model** ([spec](architecture/specs/own-vision-model.md)) + **M4 two operating points** (ADR-0014) | beats VespAI; zero bees at ACT |
| With M6 | **Attack alert** ([spec](architecture/specs/attack-alert.md)) | one alert per episode |

Brick order (owner, Q12): **C1 first**, right after this dossier; the M3 report is slotted in
while C1 hardware ships. The first C1 unit goes to the home hives (mains, Wi-Fi), a second one to
the remote apiary later.

M0–M4 below are the original staircase (M0–M2 done; M3 harness and M4 single point shipped,
M3 report open). M5 and M6 are refined by the plan above.

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

### M5 — Own data and own model

Capture with C1 → annotation pipeline → frozen test set → fine-tune a permissively licensed
pre-trained detector (ADR-0015) → compare with VespAI → measure both operating points (ADR-0014).
No longer optional: VespAI's recall does not transfer and its licence blocks a product.

**🚪 Gate** — own model beats VespAI on the frozen set; zero bees at the ACT point.

### M6 — Live / embedded *(sketch)*

`Picamera2` adapter (real-time stream) → measure FPS/latency → headless
service → NPU port (Hailo).

**🚪 Gate** — stable real-time detection on the target + measured power
draw.

## Deterrence track (v2) — gated on a field test

The deterrence axis is **decoupled** from detection (SOLID / Dependency
Inversion): it consumes the detector's signal (`Detection`) via
the ports and adds nothing to the detection core. It is gated on **D0**,
before any mechanics are built.

### D0 — Field-validate the deterrence hypothesis *(before any actuator)*

Cheap, manual, seasonal (hornets active ~Aug–Nov): manually spray a hornet
hovering at the flight board → observe whether it **breaks off and leaves**,
**returns**, or **habituates**, and log it.

**🚪 Gate** — without a clear, lasting break-off (the hornet leaves and does
not simply return or habituate), **reorient** (another deterrent modality,
or stay monitoring-only) instead of building the aiming mechanics. Efficacy objective once validated: **~90%** drop in successful
strikes (an *objective*, not a gate — see
[requirements.md](requirements.md)).

### v1 is deployable on its own

Once M3 (detection figures) and M6 (embedded) are done, the v1 monitoring
build can go to the apiary: it delivers hornet-pressure data, feeds M5
(footage), and provides the hornets D0 needs to test against. *Since 2026-10-16
the footage comes first from the C1 neutral collector, before M6 (see the
re-targeted plan).*

## Cross-cutting gate rules

- **1 step = 1 PR** (or a few), CI green, tests, decisions logged in
  `PROJECT_LOG.md`.
- **Dependencies**: M3 needs annotations (from M1/M5; field annotations come from C1); M4 needs M3; M2
  depends only on M0.
- Each gate is a **bifurcation point** — reorient without sunk cost.

## Key risk

*Realised and resolved (2026-10-16).* VespAI has no bee class (M0) and its recall does not
transfer (~3–13 % on the Roboflow set); ADR-0015 replaces it with an own model, keeping VespAI as
the baseline. The key risks now are the season deadline for C1, the D0 hypothesis and the acoustic
SNR (A0).

## Deferred tracks (out of the detection-first scope)

- **Observability & health** — model decided in
  [requirements.md](requirements.md) (detections → local log; heartbeat
  liveness; fault-only alerts; server-side dead-man's-switch watchdog).
  Implementation lands with the embedded deployment (M6).
- **Acoustic axis** — recording starts with C1; feasibility gate A0 (SNR, simple classifier)
  decides the role (confirmer, wake-up, both, none) — ADR-0016.
- **After-detection** — tracking, distance, decision policy, non-lethal
  deterrence (the deterrence track above; gated on **D0**).
- **Embedded** — see M6 and the hardware target in
  [requirements.md](requirements.md).
