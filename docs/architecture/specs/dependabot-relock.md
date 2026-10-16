# Spec — Dependabot relock of the `vision` lock (brick B7)

> **Brick**: B7 · **Decision**: ADR-0012 · **Out of scope**: new features, yolov5 vendoring,
> CI matrix changes

## Need

The `vision` lock (`requirements.txt`, compiled from `requirements.in`) carries 32 open Dependabot
alerts on 2026-10-16: 1 critical, 13 high, 13 medium, 5 low. The critical one is the `torch.load`
RCE (torch < 2.6.0). An operator who installs the `vision` extra must get versions without known
critical or high vulnerabilities, and the VespAI checkpoint must still load and detect the same.

## Actors

- **Operator** — installs the `vision` extra and runs the live detector with the VespAI weights.
- **Maintainer** — keeps the lock free of known critical/high vulnerabilities (Dependabot).

## Main scenario

1. Dependabot reports alerts on `requirements.txt`.
2. The maintainer raises the floors in the `vision` extra and `requirements.in` (ADR-0012) and
   relocks.
3. The maintainer checks every locked version against the open alert ranges.
4. The maintainer loads the real VespAI checkpoint on the old and new lock and compares detections.
5. After merge, Dependabot closes the alerts.

## Alternative scenarios

- **A1** An alert has no patched version → it closes only if the locked version leaves its range;
  otherwise the owner accepts it explicitly with a reason.
- **A2** The checkpoint fails to load or detections differ on the new lock → no merge; the bound
  that causes it is reconsidered through the ADR.
- **A3** The weights are not available → the owner explicitly accepts the AC5 gap with a reason.

## Inventory (2026-10-16)

| Package | Locked | Alerts | First fix covering all fixable alerts |
|---|---|---|---|
| torch | 2.3.0 | 1 critical, 3 medium, 5 low (3 with no fix) | 2.13.0 |
| pillow | 10.3.0 | 13 high, 5 medium | 12.3.0 (pyproject caps `<12`) |
| jinja2 | 3.1.4 | 3 medium | 3.1.6 |
| filelock | 3.14.0 | 2 medium | 3.20.3 |
| python-dotenv | 1.0.1 | 1 medium | 1.2.2 |

Three torch advisories (`<= 2.6.0`, no patched version) close as soon as torch > 2.6.0.

## Acceptance criteria

- **AC1** `pyproject.toml` `vision` extra floors: `torch>=2.13`, `torchvision>=0.28`,
  `Pillow>=12.3`; the `Pillow<12` cap is gone. Other bounds per ADR-0012.
- **AC2** `requirements.in` lists `torchvision` (the extra needs it; the lock lacked it) and the
  security floors; `requirements.txt` relocked with
  `uv pip compile -p 3.10 --strip-extras requirements.in -o requirements.txt`.
- **AC3** No locked version falls in an open alert range (checked against the alert list).
- **AC4** `make lint type-check test-unit`, `ruff format --check`, gitleaks: green.
- **AC5** With real weights: the VespAI checkpoint loads through `VespAIDetector._load`
  (weights_only=False patch) and `scripts/measure_operating_point.py` gives the same detections as
  on torch 2.3.0. If weights are not available, the owner explicitly accepts the gap with a reason.
- **AC6** After merge, Dependabot shows 0 open critical/high alerts.

## Outcome (2026-10-16)

AC1–AC6 met: PR #73. AC5 with VespAI `yolov5s-all-data.pt` on 12 example frames, byte-identical
detections on torch 2.3.0 and 2.14.1. Dependabot: 0 open alerts after merge. Evidence:
`reviews/chore-b7-dependabot-relock.md`.

## Design impact

Version bounds only; no code structure, no UML change. `_load` already forces
`weights_only=False` for the trusted local checkpoint, which is the torch ≥ 2.6 breaking change.
