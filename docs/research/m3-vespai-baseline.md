# M3 report — VespAI baseline on the Roboflow *V. crabro* / *V. velutina* set

> **Date**: 2026-10-19 · **Spec**: [`m3-report`](../architecture/specs/m3-report.md) ·
> **Related**: ADR-0002, ADR-0015 · **Recompute**: `make m3-report` (below)

## Result

VespAI (`yolov5s-all-data.pt`) scored over all 364 images (1,950 ground-truth boxes) at IoU ≥ 0.5:

### conf ≥ 0.50

| class | TP | FP | FN | precision | recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| vespa_velutina | 84 | 367 | 1259 | 0.186 | 0.063 | 0.094 |
| vespa_crabro | 8 | 87 | 599 | 0.084 | 0.013 | 0.023 |

### conf ≥ 0.80

| class | TP | FP | FN | precision | recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| vespa_velutina | 10 | 71 | 1333 | 0.123 | 0.007 | 0.014 |
| vespa_crabro | 1 | 4 | 606 | 0.200 | 0.002 | 0.003 |

**Reading.** VespAI's published F1 ≈ 0.99 does not transfer to this independent set: at the
default confidence 0.5 it finds 6.3 % of the *V. velutina* boxes, and fewer than one predicted
*V. velutina* box in five is correct. This is the baseline M5's own model must beat (ADR-0015).
Two identical runs gave byte-identical tables.

### Difference from the 2026-05-23 exploratory figures

The May measurement (throwaway scripts, not kept) reported *V. velutina* P = 0.49 / R = 0.10
(TP 129) at conf 0.5. This rerun, on the same dataset version and split sizes, with the same
weights file and inference size (640), gives P = 0.186 / R = 0.063. The May scripts are gone,
so the gap cannot be traced to one cause; the committed figures above are the reference from
now on. The conclusion is unchanged, and stronger: recall stays far below any usable level.

## Inputs

| Input | Value |
|---|---|
| Dataset | Roboflow Universe, workspace `hornet-behavior`, project [`-original-vespa-crabro-and-vespa-velutina`](https://universe.roboflow.com/hornet-behavior/-original-vespa-crabro-and-vespa-velutina/dataset/1), **version 1** (exported 2024-05-30), format YOLOv5 PyTorch |
| Dataset licence | CC BY 4.0 (attribution: hornet behavior, Roboflow Universe) |
| Dataset content | 364 images, 640×640 (stretched, auto-orient); train 255 / valid 73 / test 36; classes `0 = Vespa-Crabro`, `1 = Vespa-Velutina`; no bee class |
| Dataset archive SHA-256 | `bc3cc54f5179cb094a67866d96424e4af056796e05e8be0457289cb217536c36` (`…v1i.yolov5pytorch.zip`, 19,377,980 bytes) |
| Weights | `yolov5s-all-data.pt` from [andrw3000/vespai](https://github.com/andrw3000/vespai) `models/yolov5-params/`, repo commit `004f3d8930d19affd04f5d112224107c5d81eec4` |
| Weights SHA-256 | `1fff0bde968690917e6136077bf144dda2e03cccaa5ae0648cf2bf5cce423694` (14,369,205 bytes) |
| Weights licence | CC BY-NC-SA 4.0 — loaded from a path, never committed (ADR-0002) |
| YOLOv5 code | [ultralytics/yolov5](https://github.com/ultralytics/yolov5) at `23701eac7a7b160e478ba4bbef966d0af9348251` (VespAI's submodule pin) |
| Scoring | `aristech.evaluation` (`collect_samples` + `evaluate`), IoU ≥ 0.5, greedy class-agnostic one-to-one matching; all three splits; class map `0:vespa_crabro,1:vespa_velutina` |
| Detector floor | 0.5 (lowest reported threshold) — see "Known limits" |

## Environment

Ubuntu 24.04.5 LTS, Linux 6.8, Intel Core i9-13900H, CPU only (no GPU). Python 3.10.20,
torch 2.14.1+cpu, opencv 4.11.0, numpy 1.26.4, plus `setuptools<81` and YOLOv5's runtime
packages; the full pinned set is
[`m3-vespai-baseline-requirements.txt`](m3-vespai-baseline-requirements.txt). Run time ≈ 3 min 15 s.

## Reproduce

```bash
# 1. Inputs, outside the repo (weights are CC BY-NC-SA: never commit them)
mkdir -p ~/vespai-baseline && cd ~/vespai-baseline
git clone https://github.com/andrw3000/vespai.git
git -C vespai checkout 004f3d8930d19affd04f5d112224107c5d81eec4
git clone https://github.com/ultralytics/yolov5.git
git -C yolov5 checkout 23701eac7a7b160e478ba4bbef966d0af9348251
sha256sum vespai/models/yolov5-params/yolov5s-all-data.pt   # expect 1fff0bde…3694

# 2. Vision environment pinned to the measured run (CPU torch; the extra index serves torch only)
uv venv -p 3.10 .venv
VIRTUAL_ENV=.venv uv pip install --index-strategy unsafe-best-match \
  --extra-index-url https://download.pytorch.org/whl/cpu \
  -r "<aristech checkout>/docs/research/m3-vespai-baseline-requirements.txt"
VIRTUAL_ENV=.venv uv pip install --no-deps -e "<aristech checkout>"

# 3. Dataset: sign in to Roboflow, download version 1 as "YOLOv5 PyTorch" (zip) from the URL
#    above, then unzip it into <aristech checkout>/data/external/vespa-crabro-velutina/
#    (data/external/ is git-ignored).

# 4. Recompute (from the aristech checkout)
make m3-report PYTHON="$HOME/vespai-baseline/.venv/bin/python" \
  WEIGHTS="$HOME/vespai-baseline/vespai/models/yolov5-params/yolov5s-all-data.pt" \
  YOLOV5_DIR="$HOME/vespai-baseline/yolov5" \
  DATASET=data/external/vespa-crabro-velutina
```

The command prints the two tables above. Other thresholds, splits or IoU:
`python scripts/vespai_baseline_report.py --help`.

## Known limits

- **No bee class** in this set: bees classified as the target cannot be measured here, so the
  legal floor (M4, ADR-0014) is not exercised by this baseline.
- **Floor at the lowest threshold, not 0.** At floor 0, YOLOv5's CPU NMS exceeds its time limit
  and drops boxes. YOLOv5 filters candidates by confidence before per-class NMS, and a box below
  the floor can never suppress one above it, so the floor leaves the tables unchanged except for
  boxes at exactly 0.500 (YOLOv5 keeps `> conf`, the harness counts `>= threshold`). The runs
  logged no NMS time-limit warning at floor 0.5. Curves over the full range belong to
  `scripts/measure_operating_point.py`.
- All splits are scored together: VespAI was not trained on this set, so train/valid/test are
  all unseen data for it. `--splits test` gives the 36-image test split alone.
- Greedy, class-agnostic matching at IoU 0.5 (highest confidence first): a box on the right
  insect with the wrong species counts as a confusion (FP for the predicted class, FN for the
  true one), and a well-placed box with a loose fit counts as FP + FN.
