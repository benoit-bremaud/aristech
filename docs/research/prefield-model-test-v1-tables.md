# Pre-field model on the frozen test set

- frozen set: test-v1 (288 images), sha256 6d4f5dc56b62eaab5ed15b91e25512a1f11f5ddcc4bd447366084952f0d654d9
- manifest sha256: 35c77b53852c5b800bbc72b060ae96b3d59f77168177deaadf7bb96fe845d8b8
- RF-DETR weights sha256: 3df5a250d9cf3dc837a86376b62b634d0f693d202288a782bd46cb8cf992fcab
- VespAI weights sha256: 1fff0bde968690917e6136077bf144dda2e03cccaa5ae0648cf2bf5cce423694
- RF-DETR Small (own fine-tune): code and base weights Apache-2.0 (rfdetr 1.11.2)
- VespAI: weights CC BY-NC-SA 4.0, YOLOv5 AGPL-3.0 (comparison only)
- images: 288 · ground-truth boxes: 1032

### conf ≥ 0.50 (IoU ≥ 0.50)

| class | RF-DETR P | RF-DETR R | RF-DETR TP/FP/FN | VespAI P | VespAI R | VespAI TP/FP/FN |
|---|---:|---:|---:|---:|---:|---:|
| vespa_velutina | 0.571 | 0.480 | 97/73/105 | 0.000 | 0.000 | 0/29/202 |
| vespa_crabro | 0.885 | 0.719 | 23/3/9 | 0.016 | 0.031 | 1/61/31 |
| apis_mellifera | 0.964 | 0.860 | 671/25/109 | 0.000 | 0.000 | 0/0/780 |
| unknown | 0.545 | 0.667 | 12/10/6 | 0.000 | 0.000 | 0/0/18 |

### conf ≥ 0.80 (IoU ≥ 0.50)

| class | RF-DETR P | RF-DETR R | RF-DETR TP/FP/FN | VespAI P | VespAI R | VespAI TP/FP/FN |
|---|---:|---:|---:|---:|---:|---:|
| vespa_velutina | 0.667 | 0.010 | 2/1/200 | 0.000 | 0.000 | 0/1/202 |
| vespa_crabro | 0.917 | 0.688 | 22/2/10 | 0.250 | 0.031 | 1/3/31 |
| apis_mellifera | 0.998 | 0.674 | 526/1/254 | 0.000 | 0.000 | 0/0/780 |
| unknown | 0.600 | 0.500 | 9/6/9 | 0.000 | 0.000 | 0/0/18 |
