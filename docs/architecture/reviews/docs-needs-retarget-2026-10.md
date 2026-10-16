# Pre-push review — `docs/needs-retarget-2026-10`

> **Scope**: docs-only — needs brainstorm record, ADR-0013 to ADR-0016 (superseding 0006, 0004,
> 0002), five Proposed specs, `product/` use-case and data-flow diagrams, traceability,
> `requirements.md`, `ROADMAP.md`, `architecture.md`, index READMEs. No code, no gate (planned
> features get their gates in their own bricks).

## Checks

- Every MCDA table and sensitivity case recomputed by script; weights sum to 100. Session-time
  errors (Q2 B 425 not 450, Q3 C 285 not 310, Q1/Q2/Q7 sensitivity figures) corrected and
  disclosed in the record.
- markdownlint clean on every changed file; all new relative links resolve.
- Superseded ADRs: Status line only.

## 🔴 Must Have

None.

## 🟡 Should Have (all fixed)

- `architecture.md` still described ADR-0004 as current and fusion as fully open → pointers to
  ADR-0014 / ADR-0016.
- `requirements.md` signals table said detections are "never pushed" and called aggregated pushes
  "the wrong model" → reconciled with ADR-0013 (one episode-level alert).
- `ROADMAP.md` stale "Key risk" (VespAI classes) and pre-C1 wording → marked resolved / updated.
- Alert timing in record Q6 → aligned to "with M6".
- Traceability UC1 / UC2 rows lacked the new ADRs → added.
- Specs README did not say gates are still required → stated.

## 🔵 Nice to Have

- Fixed: recall figure reconciled (0.10 @0.5, range 3–13 %); full sensitivity weight vectors stated;
  "Device" removed as an actor; stack details moved out of `capture-rig` / `own-vision-model` to
  their brick ADRs.
- Deferred: new specs use a `Status / Milestone / Related` header vs `Brick / Audit / Related` in
  older specs (planned specs have no brick yet); harmonise when each gets its brick.

## ⚪ Disagree / Intentional

- ADR-0013 and ADR-0014 are weight-sensitive (flips disclosed); the owner chose at the validated
  weights, which per the method makes the top score the solution.
