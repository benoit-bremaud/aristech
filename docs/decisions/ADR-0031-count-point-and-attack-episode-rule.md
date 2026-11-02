# ADR-0031: COUNT point at 80 % image precision, one alert per attack episode

- Status: Accepted
- Date: 2026-11-02 (issue #149, attack-alert gate)
- Complements: ADR-0014 (two operating points), ADR-0029 (ACT threshold)

## Context

ADR-0014 defines the COUNT point as the lowest threshold whose *V. velutina* precision reaches a
target of about 95 %, to confirm at the `attack-alert` gate, and requires `COUNT ≤ ACT`. ADR-0029
showed that box precision misleads (duplicate and loose boxes) and that alerts are judged per image.
Image-level figures of RF-DETR Small on test-v1 (50 images with *V. velutina*, 238 without):

| conf | image precision | image recall | flagged target-free images |
|---:|---:|---:|---:|
| 0.15 | 0.800 | 0.96 | 12 |
| 0.40 | 0.878 | 0.86 | 6 |
| 0.45 (ACT) | 0.896 | 0.86 | 5 |
| 0.55 | 0.907 | 0.78 | 4 |
| 0.75 | 0.938 | 0.30 | 1 |

No threshold reaches 0.95, and 0.90 is only reached at 0.55, above ACT: the 95 % target is
infeasible and would break `COUNT ≤ ACT`. The spec also needs an episode rule so the beekeeper gets
one alert per attack, not one per frame (AC1).

## Options (MCDA)

Scores 0–5, totals and sensitivity computed by `mcda/adr_0031_count_point_and_episode_rule.py`
(all 1 771 weight vectors in steps of 5).

**COUNT precision target** — recall 35, false-count noise 25, consistency with ADR-0014 25,
simplicity 15.

| Option | Recall | Noise | Consistency | Simplicity | Total /500 |
|---|---|---|---|---|---|
| A. Keep ≥ 0.95 (no point exists) | 0 | 5 | 1 | 3 | 195 |
| B. Image precision ≥ 0.80 → 0.15 | 5 | 3 | 4 | 4 | **410** |
| C. Image precision ≥ 0.85 → 0.40 | 4 | 4 | 4 | 4 | 400 |
| D. COUNT = ACT = 0.45 | 4 | 4 | 2 | 5 | 365 |

Sensitivity: B first in 44 %, C 34 %, D 27 %, A 3 %. C wins once false-count noise outweighs
recall; the episode rule below absorbs isolated false frames, which is why B's extra noise is
accepted. **Chosen: B** (owner, 2026-11-02).

**Episode rule** — robustness to false frames 35, sensitivity to a real attack 30, simplicity and
testability 20, fit with the spec 15.

| Option | Robustness | Sensitivity | Simplicity | Spec | Total /500 |
|---|---|---|---|---|---|
| E1. `N` hit frames within a sliding window `W` open; `T` without that pressure closes | 4 | 4 | 4 | 5 | **415** |
| E2. First hit frame opens; `T` of silence closes | 1 | 5 | 5 | 2 | 315 |
| E3. `N` consecutive hit frames open | 5 | 2 | 4 | 3 | 360 |

Sensitivity: E1 first in 72 %, E2 21 %, E3 14 %. **Chosen: E1** (owner, 2026-11-02).

## Decision

- **COUNT point**: the lowest threshold of the sorted grid whose **image-level** *V. velutina*
  precision is at least **0.80** (`select_count_point(..., min_image_precision=0.80,
  act_threshold=ACT)`); a model whose COUNT point lies above its ACT point is rejected. On test-v1,
  RF-DETR Small (checkpoint sha256 `3df5a250…`): **0.15** (image precision 0.800, recall 0.96).
- **Hit frame**: a frame with at least one *V. velutina* at or above the COUNT point. Frames are
  counted, not boxes, so duplicate boxes do not inflate the pressure; other species never count.
- **Episode**: `N` hit frames within the last `W` open an episode and send its single alert; the
  episode closes once `T` has passed without `N` hit frames in a window, and its summary (start,
  end, peak, hit frames) is logged. The end of the stream closes an open episode.
- **Provisional values**: `N = 3`, `W = 10 s`, `T = 60 s`, in the `alert` section of
  `config/config.yaml`; set from field data (M5) as spec AC3 requires.
- **Time**: episodes run on frame timestamps; a video file is stamped with its own time, a camera
  with the wall clock, so a recorded clip replays like the live scene.

## Consequences

- 0.15 sits exactly on the 0.80 target (48 of 60 flagged images); one more false image would move
  the point to 0.20. Re-measure on the field set and for every new model, like ACT.
- ADR-0014's "≈ 95 %" is replaced by 0.80 image precision for this model family; its other rules
  stand.
- The `Notifier` port gains `notify_attack_started` and `notify_attack_ended`; no per-detection
  push exists (AC5). The push channel itself (ADR-0006, M6) stays a later adapter.
