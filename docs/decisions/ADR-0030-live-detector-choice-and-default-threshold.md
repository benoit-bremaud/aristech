# ADR-0030: Live detector choice and per-detector default ACT threshold

- Status: Accepted
- Date: 2026-11-02 (issue #140, M6)
- Complements: ADR-0009 (detector floor), ADR-0029 (ACT threshold)

## Context

The live CLI ran VespAI only, with `--confidence` defaulting to 0.5. ADR-0029 measured the ACT
threshold of the RF-DETR Small pre-field model at 0.45 on test-v1, bound to the checkpoint sha256
`3df5a250…cf992fcab`. The CLI must run either detector, and its default threshold must not hide
that a value holds only for the model it was measured on.

## Options (MCDA)

Criteria and weights: safety of the threshold 35, consistency with the ADRs 25, simplicity 25,
operator convenience 15. Scores 0–5.

| Option | Safety | ADRs | Simplicity | Convenience | Total /500 |
|---|---|---|---|---|---|
| A. One default 0.5 for both detectors | 2 | 1 | 5 | 4 | 280 |
| B. Default per detector (RF-DETR 0.45, VespAI 0.5) + warning on an unmeasured checkpoint | 5 | 5 | 4 | 5 | **475** |
| C. `--confidence` mandatory with RF-DETR | 4 | 3 | 4 | 2 | 345 |
| D. Threshold in `config.yaml`, keyed by model sha256 | 5 | 4 | 2 | 4 | 385 |

Sensitivity (`mcda/adr_0030_live_default_threshold.py`, 969 weight vectors in steps of 5): B ranks first in 99 % of them.
**Chosen: B** (owner, 2026-11-02).

## Decision

- `--detector {vespai,rfdetr}` (default `vespai`, unchanged behaviour); `--checkpoint` for RF-DETR.
- `--confidence` defaults to 0.45 for `rfdetr` (ADR-0029) and 0.5 for `vespai`.
- At start-up the CLI hashes the checkpoint; if it is not the model measured by ADR-0029 it logs a
  warning that the threshold is not a measured ACT point for it. It does not refuse to run.
- The detector floor (ADR-0009) applies to both detectors unchanged.
- Every run logs FPS and detect latency (warm-up apart, then p50 / p95).

## Consequences

- A new model means a new measurement (ADR-0029) and an update of the sha256 constant.
- Laptop CPU baseline: `docs/research/live-fps-laptop-cpu.md`.
