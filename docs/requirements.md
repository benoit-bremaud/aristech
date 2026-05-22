# Aristech — Requirements

Needs-first specification for aristech. This document defines **what** the
system must do, independent of **how** it is built. Per Dependency
Inversion applied at project level: the needs are the stable high-level
policy; the stack (board, sensors, model) is a downstream detail that must
conform to the needs — never the reverse.

Companion documents: [ROADMAP.md](ROADMAP.md) (the staged plan that
implements these needs), [architecture.md](architecture.md) (how aristech
models the world), [research/](research/) (the evidence behind the
decisions).

## Vision & goal

Protect honeybee colonies — **and the bees themselves** — by **effectively
disrupting every Asian hornet (*Vespa velutina*) that appears near the
apiary**. The hornet hovers in front of the hive landing board and picks
off returning foragers; under sustained pressure the colony stops foraging
and can collapse.

**Root need:** reduce predation pressure at the apiary, **without harming
protected species, and without daily human labour.**

## Scope

### v1 — Detection + logging

- Detect and recognise *V. velutina* at the hive entrance (vision).
- **Log** every detection locally for statistics (not a push per detection).
- **No actuator.** No spraying. Deterrence is explicitly out of v1.

> System **health** (heartbeat + fault-only alerts) is *decided* — see
> [Observability & health](#observability--health-decided) — but its
> implementation lands with the **embedded deployment (M6)**, not in v1.
> v1's health surface is the local detection log only.

### v2 and beyond (out of v1)

- Non-lethal, non-contact deterrence (water jet) — already decided as the
  direction (see [architecture.md](architecture.md)), gated on the open
  product decisions.
- Acoustic recognition axis, multi-modal fusion.
- Tracking, distance estimation, aiming.

## Functional needs

The system must, expressed as actor/system goals independent of technology:

1. **Perceive** the scene in front of the flight board continuously.
2. **Discriminate** *V. velutina* from honeybees and other insects, **with
   an explicit confidence level**.
3. **Locate** the threat in the image (2D position; 3D distance deferred to
   v2 when aiming matters).
4. **Track** a target over time (trajectory, count distinct hornets) — v2.
5. **Decide** whether to act and, if so, **deter** without contact or
   lethality, under an auditable policy with a fail-safe default — v2.
6. **Record** every detection to a structured local log (for statistics
   and later analysis) — **not** a push notification per detection.
7. **Report its own health** — a periodic heartbeat (liveness) and a
   notification only when something is wrong.
8. **Operate unattended**, outdoors, over time.
9. **Be accountable** — log its decisions and keep evidence (what it saw,
   why it acted / abstained).

## Non-functional needs

- **Near-absolute selectivity on protected species** — a false positive on
  a honeybee is unacceptable, not merely undesirable (legal, see below).
- **Energy autonomy** / no daily maintenance.
- **Robustness** to light, weather, occlusion.
- **Responsiveness** — the hornet hovers only seconds; a target latency is
  to be defined.
- **Testability / portability** — already served by the Clean Architecture
  layering (domain and use cases run with fakes, no hardware).

## Hard constraints (non-negotiable)

- **Legal floor** — harming or capturing a protected pollinator is criminal
  (Art. L411-1 + L415-3 Code de l'environnement). Consequences: the species
  classifier defaults to **abstain → do not act** below threshold; a
  geometric **no-spray exclusion zone** around the landing board is enforced
  independently of the classifier; any trap-like activity must be
  **selective**; **pure water only**, no biocide. See
  [architecture.md](architecture.md) § Plancher légal.
- **Non-lethal, non-contact** deterrence only (decided, PR #4 — see
  [architecture.md](architecture.md) § Décisions ouvertes).

## Decisions — detection (v1), with rationale

| Decision | Choice | Rationale |
| --- | --- | --- |
| Model approach | **Wrap the VespAI baseline first** ([andrw3000/vespai](https://github.com/andrw3000/vespai), YOLOv5s + ResNet, weights provided), fine-tune on own data later (hybrid) | Detect within days, no corpus/GPU needed to start; avoids blocking the whole project on data. |
| Axis order | **Vision first**, audio later | Vision is mature with a baseline; audio at a hive (thousands of bees + wind) is an unproven SNR bet to isolate later. |
| Classes (v1) | **velutina = sole target; crabro detected but non-target; bee = negative, not a positive class** | M0 finding: VespAI outputs only *V. velutina* + *V. crabro*, no bee class. Only *V. velutina* is the threat (cf. `Detection.is_threat()`); *V. crabro* (native European hornet) is detected but **non-target — do not act**. For v1 the legal floor still holds via "bee → no hornet detection → no action". An explicit bee class is deferred to fine-tuning on own data (M5). |
| Baseline licence | **VespAI is CC BY-NC-SA 4.0** — accepted for v1 | Usable for non-commercial R&D. **Blocks commercial use**; fine-tuning its weights yields a CC BY-NC-SA derivative. A permissively-licensed model is required before any product — revisit then. |
| Detection output | **2D bbox + species + confidence** (the `Detection` entity) | Free with VespAI (it outputs bboxes); survives into v2 (tracking, exclusion zone, aiming). 3D distance deferred. |
| Observation | **Fixed camera** over the flight volume | Stable background → better detection, no early mechanics. Pan/tilt belongs to v2 aiming. |
| Operating point | **~100% precision (never flag a bee / non-hornet as a target), relaxed hornet recall** | Never classify a non-hornet as a target — in v1 that means never raising a false hornet alert; in v2 the same guard gates the actuator (legal). Missing some hornets is tolerable — this is deterrence, not extermination. High confidence threshold + abstention default. |
| Evaluation | **Qualitative → quantified offline → representative → live** | A trajectory, not a single choice; numbers before trust, field validation last. |
| Data | **Inventory public → small validation set → own footage + annotation** | Public datasets unblock the start; own apiary footage is the gold data (and a publishable contribution). |

## Observability & health (decided)

The system is an **autonomous, unattended, outdoor** device. The right
notification model is therefore **operational health, not detection events**
— "no news is good news". Three distinct signal types:

| Signal | What | Channel | Cadence |
| --- | --- | --- | --- |
| **Detections** | species, position, time | **structured local log** | continuous, **never pushed** (feeds statistics + the data flywheel) |
| **Heartbeat** | "alive and functional" | periodic ping to a server | every N minutes |
| **Faults** | a problem the device can detect | **push notification** (Telegram / email) | only when something is wrong |

- **Dead man's switch** — a dead system cannot announce that it is dead, so
  liveness is judged by the **absence** of a heartbeat: a server-side
  watchdog alerts when no ping arrives within a window. The device itself
  pushes only the faults it *can* detect **and still deliver** (camera
  down, inference error, low disk / battery, …). **Connectivity loss** is
  the special case: the device cannot push when offline, so it logs it
  locally and (optionally) notifies once back online — but it is primarily
  surfaced by the watchdog seeing a missing heartbeat.
- **No per-detection notification** — that would be hundreds of pushes a
  day and is pure noise. Detections are logged for analysis instead.
- **Scope** — v1 already logs detections (the `LoggingNotifier`). The
  heartbeat + fault-alerting + the server-side watchdog land with the
  autonomous deployment (embedded phase, M6), not before.

This **supersedes the earlier provisional "alert" defaults** (Telegram
push of aggregated detections), which were the wrong model.

## Explicitly deferred (not in v1)

- **Acoustic axis** and multi-modal fusion.
- **After-detection chain**: tracking, distance, decision policy,
  deterrence (the `NeutralizeTarget` use case and its open decisions).
- **Embedded target**: real-time camera, on-device NPU, headless service.
- **UML diagrams** — held until the open product decisions stabilise the
  scope enough to be worth drawing.
- **Tech debt**: `.gitignore` inline-comment bug, agent-agnostic cleanup of
  historical log entries, `git filter-repo` blob purge, portable
  `requirements.txt`, legacy `DIY_INSTRUCTIONS.md` / `BOM.md` reconciliation.

## Hardware target (downstream of needs)

Recorded for context, **not a driver**: the foundations survey
([research/prototype-foundations.md](research/prototype-foundations.md) § C)
recommends Raspberry Pi 5 + AI HAT+ (Hailo-8L) with a Pi HQ camera and solar
power. This is the default embedded target to revisit once the v1 software
pipeline is validated on recorded video — the stack conforms to the needs,
not the reverse.
