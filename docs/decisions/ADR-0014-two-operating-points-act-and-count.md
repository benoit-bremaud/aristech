# ADR-0014: Two operating points — zero-bee to act, high precision to count

- Status: Accepted
- Date: 2026-10-16 (needs brainstorm, Q2)
- Supersedes: ADR-0004

## Context

ADR-0004 picks one threshold: the lowest at which no bee is classified as a target. It serves the
legal floor (ADR-0003) — harming a protected pollinator is a criminal offence. With ADR-0013 the
detection now feeds two different consumers:

- **Acting** (v2 deterrent): a bee wrongly targeted is a legal failure.
- **Counting and the attack alert**: no physical act on any insect, so a false positive costs only
  some statistical noise, while a crushed recall makes the counts and the alert useless.

## Options (MCDA)

Criteria and weights: legal safety 40, counting / alert quality 30, simplicity 15, consistency with
the ADRs 15. Scores 0–5.

| Option | C1 | C2 | C3 | C4 | Total /500 |
|---|---|---|---|---|---|
| A. One zero-bee threshold for everything (ADR-0004 as is) | 5 | 2 | 5 | 5 | 410 |
| B. Two measured operating points: ACT = zero-bee; COUNT = precision ≥ ~95 % on *V. velutina* | 5 | 4 | 3 | 4 | **425** |
| C. Drop zero-bee, single F1-optimal threshold | 1 | 5 | 5 | 1 | 280 |

Sensitivity (script-checked): legal 50 taken from simplicity (50/30/5/15) → B 445, A 410; legal 50
taken from quality (50/20/15/15) → **A 440, B 435**. B holds only while counting quality weighs at
least ~25. **Chosen: B** (owner, 2026-10-16).

## Decision

- **ACT point**: the lowest threshold at which zero bees are classified as target on the frozen set
  (ADR-0004's rule, unchanged); below it the decision is ABSTAIN. Only this point may ever drive an
  actuator. The geometric no-spray zone (ADR-0003) applies on top, independently.
- **COUNT point**: the lowest threshold whose *V. velutina* precision on the frozen set is at least
  the target (≈ 95 %, an estimate to confirm at the `attack-alert` gate). It drives counts,
  statistics and the attack alert, never an actuator.
- Both points are measured by the evaluation harness (`evaluation/operating_point.py` gains the
  second rule) and recorded with the model version they were measured on.
- `COUNT ≤ ACT` must hold; a model where it does not is rejected.

## Consequences

- `application/decision.py` will need the two thresholds; the ACT / ABSTAIN / IGNORE outcome stays
  the action contract. Implementation waits for its own brick and gate.
- Issue #18 (measured zero-bee threshold) still waits for an own-data set (M5).
- A future acoustic confirmer can only raise the bar to act (ADR-0016), never lower it.
