# Local review — aristech (branch `refactor/b5-yagni-training-removal`)

- Date: 2026-10-16
- Commit: 69cf340 (+ review fixes)
- Scope: branch diff `main...HEAD`
- Checks run: design · docs · tests · security · correctness
- Verdict: ship · Must 0 · Should 2 (fixed) · Nice 3 · Disagree 3

## Pre-merge gate

| Step | Result |
|---|---|
| 1 Tests | ✅ root `pytest`: 107 passed, 2 skipped (cv2 absent locally, runs in CI), 5 deselected · ruff, `ruff format --check src tests`, mypy clean · actionlint clean · integration selection needs `.env` + data (unchanged by this diff) |
| 2 Coverage | tests 93 % (floor 80) · docs: no new public API (pure move of `distribute_files`) |
| 3 SonarQube | ⚠️ Community Build analyses `main` only → run `make sonar` post-merge |
| 4 Secrets | ✅ gitleaks clean on `main..HEAD` · only `.env.example` tracked · diff read: nothing sensitive |
| 5 QA pass | ✅ CLI artefact: `python -m aristech --help` OK · `scripts/distribute_images.py` imports `aristech.datasets` and stops on the missing `.env` as designed |

- Gate: **GREEN for push** — Sonar step runs post-merge as on previous bricks.

## 🔴 Must Have
_None._

## 🟡 Should Have
- `models/README.md:5,11,22-26` `[docs][design]` · pointed to the deleted `scripts/train_model.py` and `make train` · **Fixed**: rewritten around operator-supplied VespAI weights (ADR-0010).
- `docs/architecture.md:84,88` `[design]` · listed `audio/`, `connectivity/` as planned with their extras gone · **Fixed**: marked as removed extras returning with their adapter.

## 🔵 Nice to Have
- `CLAUDE.md:37` `[design]` · example extra `audio` no longer exists · **Fixed**: `(e.g. vision)`.
- `src/aristech/datasets/distribute.py:3` `[docs]` · "sans I/O parasite" while it moves files (pre-existing wording, pure rename) · left for B6 docs pass.
- `src/aristech/datasets/__init__.py:1` `[docs]` · docstring could name the train/val/test split · left for B6.

## ⚪ Disagree / Intentional
- `pyproject.toml` `vision` extra, `requirements.in` `[correctness]` · keep `pandas`: YOLOv5 `results.pandas()` at `vespai_detector.py:129`.
- `docs/architecture.md:112-147`, `docs/ROADMAP.md:112`, `docs/requirements.md:49,160,170` `[docs]` · vision diagram and future `Target`/`NeutralizeTarget` belong to the S2 rewrite, brick B6 (spec out-of-scope).
- `docs/decisions/ADR-0001-*.md:3` `[docs]` · status line marks the supersession by ADR-0010; body untouched.

## Per-dimension summary
- Design: dependency rule holds, no speculative abstraction left, `datasets/` correctly placed. · Docs: spec, gate, ADR-0010, UML notes; stale references fixed. · Tests: distribute tests moved intact, no kept code lost coverage. · Security: dependencies only shrink, clean. · Correctness: scripts import fine, lock coherent.
