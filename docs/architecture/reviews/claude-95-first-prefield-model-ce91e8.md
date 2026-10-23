# Local review — aristech (branch claude/95-first-prefield-model-ce91e8)

- Date: 2026-10-23
- Commit: c0642ec (fixes in 57d1fc8, c0642ec)
- Scope: branch diff `main...HEAD` (issue #95, PR 4: first pre-field model)
- Checks run: design · docs · tests · security · correctness
- Verdict: ship — every Must and Should fixed · Must 2 · Should 9 · Nice 5 · Disagree 1

## Pre-merge gate (head SHA c0642ec)

| Step | Result |
|---|---|
| 1 Tests | ✅ 268 passed, 2 skipped (cv2 absent, OpenCV source; unchanged from main), 5 deselected (integration markers) |
| 2 Coverage | tests 96 % overall (aristech); new code 98.3 % (SonarQube); `export.py` and `rfdetr_detector.py` 100 % · docs ≈ 94 % (floor 90) |
| 3 SonarQube | ✅ PASSED on 57d1fc8 → c0642ec (new violations 0, new coverage 98.3 %, duplication 0 %, hotspots 100 % reviewed) |
| 4 Secrets | ✅ gitleaks clean (`main..HEAD`) · only `.env.example` tracked (placeholders) · diff read: no keys, tokens or pixels; weights stay git-ignored |
| 5 QA pass | ✅ real artefact: export (1,560 / 251 / 288), training (32 epochs, best epoch 21) and the report on test-v1; see [QA note](../qa/2026-10-23-prefield-model.md) and the [box spot check](../qa/2026-10-23-box-spot-check.csv) |

- Gate: **GREEN**

## 🔴 Must Have

- `src/aristech/datasets/export.py` `[design|security]` · `rmtree` on any `--out`: a wrong path would delete an unrelated directory · **fixed**: a non-empty directory without `data.yaml` is refused (`FileExistsError`, exit 2); `data.yaml` is written first so an interrupted export still reads as a view.
- `docs/architecture/diagrams/annotation-pipeline/05-sequence-train-score.md` `[docs]` · showed a `--size` flag that does not exist and left out `--output` and the re-export before training · **fixed**.

## 🟡 Should Have

- `export.py` `[correctness]` · a missing label left a dangling link · **fixed** (`FileNotFoundError` before writing, tested).
- `scripts/train_rfdetr.py`, `scripts/prefield_report.py`, `datasets/split.py` `[design]` · three copies of the file hash · **fixed**: `manifest.file_sha256`.
- `prefield_report.py`, `rfdetr_detector.py` `[design]` · the class map was written out three times · **fixed**: built from `CANONICAL_CLASSES` / `Species`.
- `prefield_report.py` `[correctness]` · the report did not check its view against the frozen set · **fixed**: `view_mismatches` checks image hashes and snapshot labels, exit 2 on a stale view.
- `rfdetr_detector.py` `[docs]` · contract and lazy-load behaviour not stated · **fixed**.
- `docs/architecture/qa/tools/box_spot_check.py` `[docs|correctness]` · worktree-specific example path, unused `CLASSES`, bare `next` · **fixed**: boxes labelled with their class.
- `docs/research/prefield-model-test-v1.md` `[docs]` · per-source numbers not in the generated tables · **fixed**: marked as a one-off breakdown of the local run.
- `tests/unit/datasets/test_export.py` `[tests]` · tautological `data.yaml` assertion; no tests for a missing label or a non-view `out` · **fixed**.
- `tests/unit/scripts/test_prefield_report.py` `[tests]` · no stale-view test · **fixed** (plus a missing report directory test).

## 🔵 Nice to Have

- `train_rfdetr.py` `[correctness]` · `--epochs 0` accepted · **fixed** (exit 2, tested).
- `prefield_report.py` `[correctness]` · `--out` parent checked only at write time · **fixed** (checked up front).
- `train_rfdetr.py` `[docs]` · example said `runs/` · **fixed** (`data/runs/`, git-ignored).
- `train_rfdetr.py` `[docs]` · exit codes not documented · **fixed**.
- `tests/unit/scripts/test_prefield_report.py` `[tests]` · monkeypatches `collect_samples` instead of injecting an image reader · kept: injecting a reader would add a parameter used only by tests; the patch targets a boundary (image decoding), not the domain.

## ⚪ Disagree / Intentional

- `rfdetr_detector.py` `[security]` · pickle risk when loading a checkpoint · `rfdetr.from_checkpoint` loads weights-only by default (`trust_checkpoint=False`); the adapter keeps that default; now stated in the docstring.

## Per-dimension summary

- Design: dependency rule holds (`datasets/` stdlib only, `rfdetr` lazy in infrastructure); no new port (the existing `HornetDetector` port has a second implementation).
- Docs: ADR-0024, spec AC11, diagram 05 and the research note match the code.
- Tests: unit tests on every new branch with hand-written fakes; no domain mocks.
- Security: destructive path guarded; no secrets; third-party pixels and weights stay out of git.
- Correctness: stale-view and missing-label paths now fail loudly with exit 2.
