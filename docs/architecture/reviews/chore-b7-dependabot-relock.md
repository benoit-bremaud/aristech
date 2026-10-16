# Pre-push review — chore/b7-dependabot-relock (brick B7)

- Date: 2026-10-16 · Spec: `specs/dependabot-relock.md` · ADR-0012 (option A, 435/500) ·
  Gate: `gates/dependabot-relock.md` (owner-signed)

## Diff

`pyproject.toml` (`vision` extra bounds), `requirements.in` (floors, `torchvision` added),
`requirements.txt` (relock), spec, ADR-0012, gate, this report. No code change.

| Package | Before | After |
|---|---|---|
| torch | 2.3.0 | 2.14.1 |
| torchvision | (missing from lock) | 0.29.1 |
| pillow | 10.3.0 | 12.3.0 |
| jinja2 | 3.1.4 | 3.1.6 |
| filelock | 3.14.0 | 4.1.0 |
| python-dotenv | 1.0.1 | 1.2.4 |
| numpy / opencv-python / pandas | 1.26.4 / 4.9.0.80 / 2.2.2 | unchanged |

## Checks

| AC | Check | Result |
|---|---|---|
| AC1, AC2 | Bounds and relock with `uv pip compile -p 3.10 --strip-extras` | ✅ |
| AC3 | Every locked version tested against the 32 open alert ranges (`packaging`) | ✅ 0 hits |
| AC4 | `make lint type-check test-unit` (105 passed, 2 cv2 skips); unit suite with cv2 in the new lock: 107 passed; `ruff format --check`; gitleaks (history and staged) | ✅ |
| AC5 | VespAI `yolov5s-all-data.pt` + YOLOv5 at VespAI's submodule commit `23701ea`, CPU, on 12 VespAI example frames (6 velutina, 6 crabro), conf 0.25: torch 2.3.0 vs 2.14.1 | ✅ byte-identical detections (species, confidence to 4 decimals, bbox) |
| AC5 | `tests/integration` with the real weights on the new lock | ✅ 1 passed |
| AC6 | Dependabot after merge | ⏳ post-merge |

## Findings

- **Must**: none.
- **Should**: none.
- **Nice**: the YOLOv5 commit pinned by VespAI imports `pkg_resources`, so the runtime venv needs
  `setuptools<81` (not in our lock; it lives in the operator's yolov5 environment). Worth a line in
  `docs/INSTALL.md` in a later brick. YOLOv5 prints torch deprecation warnings (16), none fatal.

Weights, the YOLOv5 clone and the frames were downloaded to a scratch folder outside the repository
(CC BY-NC-SA, never committed).
