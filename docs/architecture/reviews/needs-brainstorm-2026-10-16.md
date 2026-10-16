# Needs brainstorm and debrief — 2026-10-16

> **Scope**: re-target aristech's needs after the audit plan B0–B7, before any M3/M5 feature work.
> **Participants**: the owner (decides), the design assistant (proposes, scores).
> **Method**: one question at a time, need stated before any solution, MCDA matrix per choice
> (weights /100, scores 0–5, totals /500, sensitivity check), the owner picks.
> **Outputs**: ADR-0013 to ADR-0016, specs `attack-alert`, `own-vision-model`, `capture-rig`,
> `acoustic-feasibility`, `deterrence-field-test`, diagrams `product/`, updated
> `requirements.md` and `ROADMAP.md`.

## Inputs

- Audit plan B0–B7 merged (base clean, 0 Dependabot alerts).
- Measured: VespAI recall on a Roboflow *V. velutina* / *V. crabro* set is ~3–13 % (conf 0.8 →
  0.5); its claimed F1 ≈ 0.99 does not transfer. Its weights are CC BY-NC-SA, which blocks any
  product.
- Owner wish (2026-10-16): an own recognition model, combining image **and** sound.

## Q1 — Detection goal for the beekeeper

Need: what service the beekeeper actually gets — alert, count, deter, evidence.

| Criterion (weight) | A. Monitoring only (count + log + evidence) | B. A + aggregated "attack in progress" alert | C. A + automatic deterrence |
|---|---|---|---|
| Value to the beekeeper (30) | 3 | 4 | 5 |
| Legal / bee risk (25) | 5 | 5 | 2 |
| Feasibility now (25) | 5 | 4 | 1 |
| Data collection (20) | 5 | 5 | 4 |
| **Total /500** | 440 | **445** | 305 |

Sensitivity (script-checked): value 40 / feasibility 15 → B 445, A 420; feasibility 35 / value 20 → **A 460, B 445 (flip)**. B wins at the owner-validated weights but the A/B margin is thin: B is worth it only while the beekeeper's ability to react is valued above build effort.
**Decision: B** → [ADR-0013](../../decisions/ADR-0013-monitoring-with-aggregated-attack-alert.md),
spec [attack-alert](../specs/attack-alert.md).

## Q2 — Legal floor and zero-bee operating point

Need: keep the criminal-law floor (never act on a bee) without crushing the recall of counting,
where a false positive has no legal cost.

| Criterion (weight) | A. One zero-bee threshold everywhere | B. Two operating points: zero-bee to act, precision ≥ ~95 % to count / alert | C. Drop zero-bee |
|---|---|---|---|
| Legal safety (40) | 5 | 5 | 1 |
| Counting / alert quality (30) | 2 | 4 | 5 |
| Simplicity (15) | 5 | 3 | 5 |
| Consistency with ADRs (15) | 5 | 4 | 1 |
| **Total /500** | 410 | **425** | 280 |

Sensitivity (script-checked): legal 50 taken from simplicity (50/30/5/15) → B 445, A 410; legal 50 taken from quality (50/20/15/15) → **A 440, B 435 (flip)**; quality 20 / simplicity 25 → A 440, B 415. B holds only while counting quality weighs ≥ ~25: the decision rests on the beekeeper valuing useful counts.
**Decision: B** → [ADR-0014](../../decisions/ADR-0014-two-operating-points-act-and-count.md)
(supersedes ADR-0004). The geometric no-spray zone (ADR-0003) is unchanged.

## Q3 — Deterrent scope and timing (UC5)

Need: know whether a non-lethal jet deters *V. velutina* before spending months on aiming.
The owner asked for the detailed analysis (outcomes of D0, alternative modalities — air puff,
sound, passive muzzle — and what each option implies) before choosing.

| Criterion (weight) | A. Keep v2 decoupled, manual D0 as soon as possible, no engineering before | B. Freeze deterrence until after M5 | C. Drop it, monitoring-only product |
|---|---|---|---|
| Long-term value (30) | 5 | 4 | 2 |
| Cost / risk now (30) | 4 | 5 | 5 |
| Information gained (25) | 5 | 2 | 0 |
| Focus on detection (15) | 4 | 5 | 5 |
| **Total /500** | **455** | 395 | 285 |

Sensitivity (script-checked): weights 25/20/10/45 (value/cost/information/focus) → B 445, A 435 (flip); A stays first for any focus weight up to ~35.
**Decision: A** — ADR-0005 stands unchanged; D0 gets a written, dated protocol:
spec [deterrence-field-test](../specs/deterrence-field-test.md) (late 2026 if hornets are still
active, otherwise summer 2027).

## Q4 — Own vision model strategy

Need: recognise *V. velutina*, *V. crabro* and the honeybee in **our** conditions, under a licence
that does not block a product. Note: the Ultralytics YOLO implementations are AGPL-3.0, so the base
must be chosen among permissive ones (e.g. YOLOX / RT-DETR Apache-2.0, torchvision BSD); exact
licences are verified in the M5 ADR. The owner asked for the detailed analysis (pre-training vs
fine-tuning, data volumes, collection and annotation plan, licences, compute) before choosing.

| Criterion (weight) | A. Fine-tune VespAI weights | B. Permissive pre-trained base fine-tuned on own + CC BY public data | C. Train from scratch |
|---|---|---|---|
| Licence freedom (30) | 0 | 5 | 5 |
| Accuracy with little data (30) | 4 | 4 | 1 |
| Effort (20) | 5 | 3 | 1 |
| Edge deployment, Hailo (20) | 4 | 4 | 3 |
| **Total /500** | 300 | **410** | 260 |

Sensitivity (script-checked): effort 30 / licence 20 → B 390, A 350; weights 10/30/30/30 → A 390, B 380 (flip, i.e. giving up any product).
**Decision: B** → [ADR-0015](../../decisions/ADR-0015-own-vision-model-on-permissive-base.md)
(supersedes ADR-0002); VespAI stays as the comparison baseline. Spec
[own-vision-model](../specs/own-vision-model.md).

## Q5 — Audio recognition and fusion

Need: more confidence before acting and robustness when vision is poor. Known signals (literature,
to confirm locally): hornet wingbeat fundamental lower than the bee's; colony shimmering / hissing
under attack. Unknown: the signal-to-noise ratio at a real hive. No public synchronised audio+video
dataset. The owner asked for the detailed analysis (signals, mic hardware, synchronisation,
feasibility gate, fusion rules, architecture) before choosing.

| Criterion (weight) | A. Design fusion now, build after M5 | B. Synchronised audio+video collection now, A0 feasibility gate, role decided on data | C. Audio as wake-up trigger | D. No audio |
|---|---|---|---|---|
| Risk reduction / information (30) | 3 | 5 | 2 | 0 |
| Cost now (20) | 3 | 4 | 3 | 5 |
| Value potential (25) | 5 | 4 | 3 | 0 |
| YAGNI / architecture (25) | 3 | 5 | 3 | 5 |
| **Total /500** | 350 | **455** | 270 | 225 |

Sensitivity (script-checked): cost 30 / YAGNI 15 → B 445; value potential 50 → B 435, A 400. B stays first.
**Decision: B** → [ADR-0016](../../decisions/ADR-0016-acoustic-axis-collect-then-gate.md), specs
[capture-rig](../specs/capture-rig.md) and [acoustic-feasibility](../specs/acoustic-feasibility.md).
Standing rule: in the action path, audio may only reinforce abstention, never force an action.

## Q6 — Phasing and next milestones

Need: own model, A0 and D0 all depend on field data, and hornets are active only August–November;
a capture rig must be ready by July 2027.

| Criterion (weight) | A. Capture rig first (winter: M3 report → rig C1 → annotation; season 2027: capture + D0 + A0; autumn 2027: M5 + M4 two points; alert with M6) | B. Model on public data first, rig later | C. Full embedded M6 first |
|---|---|---|---|
| Season deadline (35) | 5 | 2 | 3 |
| Risk reduction (25) | 5 | 3 | 2 |
| Value delivered (20) | 4 | 3 | 4 |
| Effort / complexity (20) | 3 | 4 | 2 |
| **Total /500** | **440** | 285 | 275 |

Sensitivity (script-checked): season 20 / risk 30 / value 25 / effort 25 → A 425, B 305. A stays first.
**Decision: A** → `ROADMAP.md` (new "Re-targeted plan 2026-10" section). Hardware target unchanged
(Raspberry Pi 5 + AI HAT+ Hailo-8L), downstream of the needs.

## Q7 — Form of the neutral collector prototype (owner idea, raised during Q6)

The owner proposed to first build a **neutral prototype** that only records photos and sound near
the hives to gather real training data — which is exactly C1 of Q6 — and imagined it as a
**watchtower** ("mirador") on a stake: a flared, covered top with **slits** ("meurtrières") through
which the camera films and the microphone records, possibly **rotating inside for 360°** coverage.
The owner asked for the detailed analysis (hover volume, geometry, enclosure, rotation drawbacks,
one vs several hives) before choosing.

| Criterion (weight) | A. Fixed watchtower, one slit aimed at one entrance; enclosure designed for more slits | B. Rotating 360° watchtower | C. Fixed watchtower, one camera + mic per neighbouring hive from the start |
|---|---|---|---|
| Training-data quality (35) | 5 | 2 | 5 |
| Simplicity / unattended robustness (25) | 5 | 1 | 3 |
| Coverage (20) | 2 | 5 | 4 |
| Audio quality (20) | 5 | 1 | 4 |
| **Total /500** | **440** | 215 | 410 |

Sensitivity (script-checked): coverage 40 / data 25 / simplicity 15 → **C 410, A 380 (flip)**,
B 285; B stays last. A wins while data quality and robustness dominate — true for a first prototype.
In session the flip figures were stated as 375 / 405; corrected here.
**Decision: A**, extensible to C (blanked slits). Rotation is reserved for v2 aiming on a separate
unit: a motor beside the microphone pollutes the wingbeat band and a moving background degrades
training data. The second (colony) microphone touches the hive by cable, outside the watchtower.
Recorded in spec [capture-rig](../specs/capture-rig.md).

## Score corrections

Totals and sensitivity checks were recomputed by script after the session: Q2 option B is 425
(stated 450 in session) and Q3 option C 285 (stated 310); the Q1 and Q2 sensitivity claims made in
session were wrong and are replaced above. No ranking at the owner-validated weights changed; the
owner was told.

## Estimates vs facts

- Facts: VespAI recall figures (measured 2026-05-23, throwaway scripts — to be made reproducible by
  the M3 report brick), VespAI licence, Ultralytics AGPL licence.
- Estimates: all MCDA scores; data volumes (~1 500–3 000 boxes per class for a first model);
  wingbeat frequency bands; the ~95 % counting precision target (to confirm at the
  `attack-alert` gate).

## Out of scope of this session

- Dependabot PR #80 (pyyaml, pandas, setuptools), left open by the owner.
- Any implementation code.
