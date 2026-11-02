# Spec — operating point: the measured ACT threshold

> **Brick**: M4 · **Related**: ADR-0003, ADR-0014, ADR-0029, issue #18

## Need

The operator must start live detection with an ACT threshold that is measured, not guessed: on the
frozen set, no bee is classified as *V. velutina* at or above it, few target-free images raise an
alert, the residual risk is stated as a bound, and the number is tied to the model and the set it
was measured on.

## Actors

- **Operator** — measures the threshold with the evaluation script and passes it to the live CLI.

## Main scenario

1. The operator runs `scripts/measure_operating_point.py` with a model checkpoint and a frozen set.
2. The system runs the detector once at confidence 0 and prints, per threshold (0.05 → 0.95),
   *V. velutina* precision, recall, F1, the number of bees classified as target and the share of
   target-free images that raise an alert.
3. The system picks the ACT threshold (ADR-0029) and prints it with the bee count and the 95 % bound.
4. The operator records the result in `docs/research/` and passes it to the live CLI `--confidence`.

## Alternative scenario

- 3a. No threshold has zero bees as target with one step of margin and at most 2.5 % false-alert
  images: the script exits 1 and names the legal floor; the model is rejected for acting.

## Acceptance criteria

- **AC1** — the sweep reports precision, recall, bees as target and the false-alert rate for every
  threshold of the grid.
- **AC2** — the chosen threshold and the grid point below it both have zero bees as target, and
  the chosen threshold's false-alert rate is at most the cap.
- **AC3** — the bound 3 / n is reported with n, the number of ground-truth bees.
- **AC4** — no threshold is chosen when the margin cannot be met (exit 1).
- **AC5** — below the threshold a target abstains, at or above it acts (existing `decide`, ADR-0009).
- **AC6** — on test-v1 with RF-DETR Small, zero bees are classified as target at the chosen threshold.
