# Operating point of RF-DETR Small on test-v1

The provisional ACT threshold of the pre-field model is **0.45**: zero of 780 bees classified as
*V. velutina* at or above it (95 % bound ≤ 0.38 %), 2.1 % of the target-free images raise an alert,
and 86 % of the images with a hornet are caught (ADR-0029, issue #18).

## Inputs

- Frozen set: test-v1 (288 images, 1032 boxes: 780 bees; 50 images with *V. velutina*, 238 without),
  sha256 `6d4f5dc56b62eaab5ed15b91e25512a1f11f5ddcc4bd447366084952f0d654d9`.
- Model: RF-DETR Small fine-tune (ADR-0024), checkpoint sha256
  `3df5a250d9cf3dc837a86376b62b634d0f693d202288a782bd46cb8cf992fcab`, rfdetr 1.11.2, CPU,
  Python 3.11.
- Matching: IoU ≥ 0.5; detector run once at confidence 0.

Reproduce (needs the checkpoint and the exported view, so local only):

```bash
python scripts/measure_operating_point.py --detector rfdetr \
    --weights data/runs/prefield-small/checkpoint_best_total.pth \
    --dataset data/views/prefield --splits test-v1 \
    --class-map 0:vespa_velutina,1:vespa_crabro,2:apis_mellifera,3:unknown
```

## Box-level sweep (script output)

*V. velutina* precision, recall and F1 per box; bees classified as target; share of target-free
images with a target prediction (false alerts).

| conf | P | R | F1 | bees → target | false alerts |
|---:|---:|---:|---:|---:|---:|
| 0.05 | 0.095 | 0.797 | 0.169 | 0 | 0.071 |
| 0.10 | 0.199 | 0.738 | 0.313 | 0 | 0.055 |
| 0.15 | 0.272 | 0.698 | 0.391 | 0 | 0.050 |
| 0.20 | 0.341 | 0.668 | 0.452 | 0 | 0.042 |
| 0.25 | 0.382 | 0.639 | 0.478 | 0 | 0.038 |
| 0.30 | 0.423 | 0.614 | 0.501 | 0 | 0.034 |
| 0.35 | 0.467 | 0.589 | 0.521 | 0 | 0.034 |
| 0.40 | 0.493 | 0.550 | 0.520 | 0 | 0.025 |
| **0.45** | **0.522** | **0.520** | **0.521** | **0** | **0.021** |
| 0.50 | 0.571 | 0.480 | 0.522 | 0 | 0.021 |
| 0.55 | 0.640 | 0.431 | 0.515 | 0 | 0.017 |
| 0.60 | 0.692 | 0.366 | 0.479 | 0 | 0.017 |
| 0.65 | 0.706 | 0.297 | 0.418 | 0 | 0.017 |
| 0.70 | 0.800 | 0.198 | 0.317 | 0 | 0.013 |
| 0.75 | 0.895 | 0.084 | 0.154 | 0 | 0.004 |
| 0.80 | 0.667 | 0.010 | 0.020 | 0 | 0.004 |
| 0.85 | 0.500 | 0.005 | 0.010 | 0 | 0.004 |
| 0.90 | 0.000 | 0.000 | 0.000 | 0 | 0.000 |
| 0.95 | 0.000 | 0.000 | 0.000 | 0 | 0.000 |

## Image-level view

An alert is raised per image, so the image figures are the ones the decision weighs.

| conf | images with a hornet caught (of 50) | false-alert images (of 238) | image precision |
|---:|---:|---:|---:|
| 0.10 | 0.96 | 13 | 0.79 |
| 0.30 | 0.86 | 8 | 0.84 |
| 0.40 | 0.86 | 6 | 0.88 |
| **0.45** | **0.86** | **5** | **0.90** |
| 0.50 | 0.84 | 5 | 0.89 |
| 0.70 | 0.52 | 3 | 0.90 |

## What predicted *V. velutina* boxes really are

True class of the boxes predicted *V. velutina*, per threshold. "background" is a box matching no
ground truth at IoU 0.5: mostly a duplicate or a loose box on a real hornet, which is why box
precision understates image precision.

| conf | velutina | background | crabro | unknown | bee |
|---:|---:|---:|---:|---:|---:|
| 0.10 | 149 | 593 | 3 | 4 | 0 |
| 0.30 | 124 | 164 | 3 | 2 | 0 |
| 0.50 | 97 | 68 | 3 | 2 | 0 |
| 0.70 | 40 | 7 | 2 | 1 | 0 |

## Result and limits

- Gate of issue #18: at 0.45, **zero bees are classified as target** on test-v1, and none at any
  threshold of the grid; the rule-of-three bound on the rate is 3 / 780 ≤ 0.38 %.
- The zero-bee rule does not bind on this set, so the false-alert cap decides; 0.40 misses it by
  one image (6/238 = 2.52 %).
- Provisional: test-v1 is internet imagery, not the hive entrance. Re-measure on the field set
  (M5) and for every new model; the live default (`--confidence`) is not changed by this brick.
