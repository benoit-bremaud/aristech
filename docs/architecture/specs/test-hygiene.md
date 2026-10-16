# Spec — test hygiene (brick B3)

> **Brick**: B3 · **Audit**: M1, M2, S5, S7, N3, N4 · **Deferred from B4**: Nice items of
> `reviews/fix-b4-double-threshold.md` · **Out of scope**: S6 (`tests/model_training/` dies with
> `training/` in B5)

## Need

A developer runs `pytest` at the repository root and gets a meaningful, green result without
tensorflow, torch, cv2, a `.env` or real data. CI runs every test that needs none of those. The
tests assert the behaviour precisely enough that a regression turns them red.

## Acceptance criteria

- **AC1** Root `pytest` collects with zero errors when tensorflow is absent (M1).
- **AC2** Root `pytest` deselects `integration` and `e2e` by default; `make test-integration`
  still selects them (M2).
- **AC3** Fast `tmp_path` tests live under `tests/unit/` and carry no `integration` marker; CI runs
  the default selection, so `tests/config` YAML checks run in CI (S7).
- **AC4** `VespAIDetector._load` / `detect` are unit-tested with hand-written fake `torch` and
  `cv2` modules (the boundary), including the restore of `torch.load` when loading fails (S5).
- **AC5** The OpenCV source test asserts the exact frame count written (N3). CI installs
  `opencv-python-headless` so it runs on every PR.
- **AC6** `select_operating_point` returns `bees_as_target == 0` on every scenario where it succeeds
  (parametrised invariant, N4).
- **AC7** CLI: floor == confidence and floor == 0 are accepted and reach the detector; each wiring
  assertion lives in its own test (B4 Nice).
- **AC8** The ACT log line does not contain `abstain` (B4 Nice).

## Running deselected tests

The default `-m` also filters explicit paths: run `pytest -m integration <path>` (or
`make test-integration`) to execute an integration test.

## Design impact

Tests, `pyproject.toml` pytest options and the CI unit-test step only. No production code, no UML
change, no ADR (no structuring decision: the fix follows the existing `importorskip` pattern).
