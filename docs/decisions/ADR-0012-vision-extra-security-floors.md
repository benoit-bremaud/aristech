# ADR-0012: Security floors for the `vision` extra (Dependabot relock)

- Status: Accepted
- Date: 2026-10-16 (brick B7)
- Amends: the `vision` extra bounds of ADR-0001 (version bounds only)

## Context

32 open Dependabot alerts sit in `requirements.txt`, the lock of the `vision` extra (spec:
`docs/architecture/specs/dependabot-relock.md`). torch < 2.6.0 has a critical `torch.load` RCE;
torch ≥ 2.6 defaults `torch.load(weights_only=True)`, which `VespAIDetector._load` already
overrides for the trusted checkpoint. Pillow needs 12.3.0, above the current `<12` cap. The newest
resolvable lock also moves numpy 1.26 → 2.2 and opencv-python 4.9 → 5.0, two majors that the
alerts do not require.

## Decision — how far to move the lock

Criteria and weights: closes critical/high alerts 40, risk to VespAI/yolov5 loading and detections
30, maintenance (fewer future alerts, fewer pins) 15, diff size / reviewability 15.

| Option | C1 | C2 | C3 | C4 | Total /500 |
|---|---|---|---|---|---|
| A. Security floors (torch ≥ 2.13, Pillow ≥ 12.3, jinja2/filelock/dotenv patched), keep `numpy<2` and `opencv-python<5` | 5 | 4 | 4 | 4 | **435** |
| B. Everything to latest (numpy 2, opencv 5, torch 2.14) | 5 | 2 | 5 | 2 | 365 |
| C. Minimum: torch ≥ 2.6 + Pillow ≥ 12.3 only | 4 | 4 | 2 | 5 | 385 |

- A closes every fixable alert (all lows included, torch 2.14.1 is locked) while holding back the
  numpy 2 / opencv 5 majors that yolov5 code paths and `cv2` calls may not tolerate.
- B adds two unrequested majors to the riskiest brick of the plan.
- C leaves 4 torch medium/low alerts open (fixes in 2.7.1–2.13) for no risk gain: the
  `weights_only` break happens at 2.6 either way.

Sensitivity: with risk weighted 45 (closure 30), A = 435 → 440, C = 405, B = 335; A stays first.
Scores are estimates until AC5 (real-weights check) runs. **Chosen: A** (owner, 2026-10-16).

## Consequences

- `vision` extra: `torch>=2.13,<3`, `torchvision>=0.28,<1`, `Pillow>=12.3,<13`,
  `numpy>=1.26,<2`, `opencv-python>=4.9,<5`; numpy 2 / opencv 5 come later through their own ADR.
- `torch.load` on untrusted files is safe by default again; aristech still opts out for the
  trusted, path-loaded VespAI checkpoint (unchanged).
- Remaining risk: yolov5 on torch 2.14 (deprecation warnings such as `torch.cuda.amp.autocast`
  are expected; failure would block the merge).
