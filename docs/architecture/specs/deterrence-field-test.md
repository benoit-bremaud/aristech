# Spec — D0: field test of the deterrence hypothesis

> **Status**: Proposed (needs brainstorm 2026-10-16) · **Milestone**: D0, late 2026 if hornets are
> still active, otherwise August–November 2027 · **Related**: ADR-0005, ADR-0003, UC5

## Need

Know whether a non-lethal jet of pure water makes a hovering *V. velutina* break off and **stay
away**, before any actuator or aiming engineering (risk #1 of the project). This is a manual field
protocol, not a system feature.

## Actors

- **Researcher** (primary) — sprays and records.
- **Beekeeper** — hosts the test and keeps the colony safe.

## Optional enclosure pre-test (captive lab, needs brainstorm Q9)

Off-season, captive *V. velutina* in an enclosure **with no bee present** are sprayed with pure
water to observe the immediate reaction, the time before resuming flight and habituation over
repeated trials. It partly de-risks the hypothesis early; it **does not replace** the field D0,
because hunting behaviour at a hive entrance cannot be reproduced in a cage.

## Main scenario

1. At a hive under hornet pressure, the researcher stands outside the landing-board exclusion zone
   with a hand sprayer of **pure water**.
2. For each hovering hornet targeted (aim: ~20 trials), they record: hit or not, immediate reaction
   (leaves / ignores), time before it returns, number of returns in the next 10 minutes.
3. A control period without spraying is recorded at the same hive for comparison.
4. Ideally the session is filmed with the capture rig, which also feeds the training data.
5. Results go into a dated research note and the gate decision.

## Alternative scenarios

- **A1** No hornet activity on test days → retry; past mid-November, postpone to 2027.
- **A2** A bee is in the spray path → no spray (legal floor, ADR-0003).
- **A3** Hornets return within seconds or habituate → gate fails: reorient (other modality —
  air puff, passive muzzle — or monitoring-only) and record it in an ADR.

## Acceptance criteria

- **AC1** The protocol and the pass criterion ("lasting break-off": e.g. median time before return
  well above the control's hover interval) are written down before the first trial.
- **AC2** No spray ever reaches the landing-board exclusion zone; no additive in the water.
- **AC3** Every trial is logged (time, outcome, return time), and the summary is reproducible from
  that log.
- **AC4** The gate outcome (pass / fail / inconclusive) is recorded in `PROJECT_LOG.md` and, if
  it changes the direction, in a new ADR superseding ADR-0005.
