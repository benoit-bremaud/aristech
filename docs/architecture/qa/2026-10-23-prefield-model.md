# QA — pre-field model PR 4 (export, RF-DETR training, report), 2026-10-23

There is no UI. This pass runs the documented commands on the real data and checks what they
produce. Pixels and weights stay git-ignored under `data/`; nothing but text is committed.

## Box spot check (ADR-0024 D3)

- `docs/architecture/qa/tools/box_spot_check.py --seed 0` drew 30 iNaturalist images (10
  velutina, 10 crabro, 10 other) with their boxes on one contact sheet. The sheet stays
  outside the repo because it contains third-party pixels. The sampled hashes are in
  `2026-10-23-box-spot-check.csv`.
- Owner verdict: **all 30 correct** (2026-10-23). The agent noted that #1 and #5 are a little
  loose; both were kept. This closes the PR 3 limit "no human box check".

## Export (AC11, AC5)

- `scripts/dataset.py --store <PR 3 store> export --out data/views/prefield` → train 1,560,
  valid 251, test-v1 288. These match the PR 3 split table. `data.yaml` lists the four
  classes in canonical order. The view sits under git-ignored `data/` (checked with
  `git check-ignore`).
- The unit tests cover the refusal paths (a frozen image moved to train, an edited frozen
  file, a missing image).

## Training (AC7)

- Environment: a dedicated venv with `rfdetr[train]==1.11.2`, torch 2.14.1+cu130 and an
  RTX 4070 Laptop; frozen in `docs/research/prefield-model-requirements.txt`.
- A 1-epoch smoke run first confirmed the pipeline end to end. The model's class names are the
  canonical four, in order, at 512 px.
- `make prefield-train` ran 32 epochs in about 49 min. The auto-batch probe chose 4 × 4
  accumulation. Early stopping kept epoch 21 (EMA validation mAP 0.557). Checkpoint sha256
  `3df5a250d9cf3dc837a86376b62b634d0f693d202288a782bd46cb8cf992fcab`.

## Report (AC8)

- `make prefield-report` exit 0 → `docs/research/prefield-model-test-v1-tables.md` (generated)
  and the reading in `docs/research/prefield-model-test-v1.md`.
- VespAI runs in the same venv. YOLOv5 imports `pkg_resources`, so the venv needs
  `setuptools<81`.
- At conf 0.5: velutina P 0.571 / R 0.480 (VespAI 0 / 0), crabro 0.885 / 0.719, bees
  0.964 / 0.860, and **0 bees predicted as a hornet**.

## Known limits

- test-v1 is pre-field (public images; the bees come from one board). It cannot pass the M5 gate.
- Velutina recall is the weak point: most misses are in the crowded Roboflow apiary frames.
