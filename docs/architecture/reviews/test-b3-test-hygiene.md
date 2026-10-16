# Local review — aristech (brick B3, test hygiene)

- Date: 2026-10-16
- Scope: branch diff `main...test/b3-test-hygiene` (spec `test-hygiene`, AC1–AC8)
- Checks run: tests (dedicated audit) · correctness · security (gitleaks + diff read) · design/docs
  proportional (tests and tooling only, no production code)
- Verdict: ship after the review fixes (applied) · Must 0 · Should 4 (4 fixed) · Nice 5 (1 fixed)

## Pre-merge gate

| Step | Result |
|---|---|
| 1 Tests | ✅ root `pytest`: 118 passed, 7 skipped (tensorflow/cv2 absent), 5 deselected (integration), 0 collection errors · ruff, `ruff format --check`, mypy clean · actionlint clean |
| 2 Coverage | tests 88 % (floor 80) · `vespai_detector.py` 100 % (was untested) · docs: no production code changed |
| 3 SonarQube | ⚠️ Community Build analyses `main` only → run `make sonar` post-merge |
| 4 Secrets | ✅ gitleaks clean on the staged diff · only `.env.example` tracked · diff read: nothing sensitive |
| 5 QA pass | ✅ CLI artefact: `python -m aristech.interface.cli.main --help` OK; tooling diff, no runtime change |

## 🔴 Must Have
_None._

## 🟡 Should Have
- `tests/unit/infrastructure/test_opencv_video_source.py:21` `[tests]` · AC5 needs cv2, skipped in CI · **Fixed**: spec states AC5 is local-only (vision extra).
- `tests/unit/evaluation/test_operating_point.py` `[tests]` · invariant was near-tautological (selector filters on the same field) · **Fixed**: expected threshold per scenario + independent `evaluate` recount.
- `pyproject.toml:107` `[docs]` · default `-m` also filters explicit paths · **Fixed**: spec section and Makefile comment (`pytest -m integration <path>`).
- `Makefile` `[tests]` · `make sonar` covered `tests/unit` only while CI runs the default selection · **Fixed**: aligned to `pytest -q`.

## 🔵 Nice to Have
- `tests/unit/interface/test_cli_wiring.py` `[tests]` · `_run` ignored the return code · **Fixed**: asserts `rc == 0`.
- `tests/unit/infrastructure/test_logging_notifier.py:20` `[tests]` · `"abstain" not in` could target the record message · kept, acceptable.
- `tests/unit/infrastructure/test_vespai_detector.py` `[tests]` · `_verbose=False` not asserted · cosmetic, kept.
- `.github/workflows/ci.yml` `[tests]` · future unmarked heavy tests outside `tests/unit` would turn CI red · accepted: that is the desired signal.
- `tests/unit/training/test_distribute.py` `[tests]` · seeded split, repeatable · no change.

## ⚪ Disagree / Intentional
- S6 (`tests/model_training/` false-confidence tests) · deferred to B5, which removes `training/`.

## Per-dimension summary
- Design: tests only, fakes at the torch/cv2 boundary. · Docs: spec + gate added. · Tests: pyramid moves toward unit, no domain mock. · Security: clean. · Correctness: no finding.
