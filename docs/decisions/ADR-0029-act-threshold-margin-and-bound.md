# ADR-0029: ACT threshold — zero bees with margin, false-alert cap, rule-of-three bound

- Status: Accepted
- Date: 2026-11-02 (issue #18, M4)
- Complements: ADR-0014 (two operating points)

## Context

ADR-0014 defines the ACT point as the lowest threshold at which zero bees are classified as target
on the frozen set. Measuring it on test-v1 (288 internet images, 780 bee boxes, 50 images with
*V. velutina*, 238 without) with RF-DETR Small showed three gaps:

- no bee is ever classified as target, even at 0.05: the zero-bee rule alone does not bind and
  picks the lowest threshold of the grid, where 5.5 % of target-free images raise an alert, against
  the requirement "never classify a non-hornet as a target" (`requirements.md` § Operating point);
- box-level precision misleads (0.20 at 0.10): most false boxes are duplicates or loose boxes on a
  real hornet; an alert is raised per image, so the false-alert cost is image-level;
- zero bees on n bees only bounds the rate; and a threshold right at the edge of the last bee
  misread has no headroom.

## Options (MCDA)

The legal floor (zero bees as target) is a hard constraint, met by every option, so it is not a
criterion. Criteria and weights, from `requirements.md` (precision first, recall relaxed): false
alerts per image 40, hornet recall per image 35, consistency with the ADRs and requirements 25.
Scores 0–5; image figures on test-v1.

| Option | False alerts | Recall | Consistency | Total /500 |
|---|---|---|---|---|
| A. Zero bees with margin only → 0.10 (13/238 false, R 0.96) | 2 | 5 | 3 | 330 |
| B. Also box precision ≥ 0.80 → 0.70 (3/238, R 0.52) | 4 | 1 | 3 | 270 |
| C. Also image false alerts ≤ 2.5 % → 0.45 (5/238, R 0.86) | 3 | 4 | 4 | **360** |
| D. Fixed 0.40 (6/238, R 0.86) | 3 | 4 | 3 | 335 |

Sensitivity (script-checked, all 171 weight vectors in steps of 5): C ranks first in 70 % of them,
A in 26 %, B in 12 % (ties counted for each). A wins only when recall outweighs false alerts plus
consistency; B only when false alerts weigh 60 or more. A first matrix with the legal floor as a
criterion is not kept: a criterion every option maxes out only inflates totals. **Chosen: C**
(owner, 2026-11-02).

## Decision

- **ACT threshold**: on a sorted grid (0.05 → 0.95, step 0.05), the threshold with the best
  *V. velutina* recall such that (1) it **and the grid point just below it** have zero bees
  classified as target, and (2) at most **2.5 %** of the target-free images get a target
  prediction at or above it (`select_operating_point(..., margin_steps=1,
  max_false_alert_rate=0.025)`).
- **Known bound**: every ACT threshold is published with the 95 % rule-of-three upper bound on the
  bees-as-target rate, 3 / n for n ground-truth bees.
- **Provisional**: a threshold measured on test-v1 is recorded with the model checksum and the set
  digest and holds only until the field set (M5) exists; it is re-measured for every new model.
- The COUNT point (ADR-0014) is not measured here; it is due at the `attack-alert` gate.

## Consequences

- On test-v1 the rule gives **0.45** for RF-DETR Small (`docs/research/operating-point-test-v1.md`).
- 0.40 misses the cap by one image (6/238 = 2.52 %): on 238 negatives the cap is coarse; the field
  set must be larger.
- `scripts/measure_operating_point.py` runs RF-DETR as well as VespAI and prints the bound and the
  false-alert rate per threshold.
