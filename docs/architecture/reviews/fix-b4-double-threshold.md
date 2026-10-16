# Local review — aristech (branch diff main...fix/b4-double-threshold)

- Date: 2026-10-16
- Commit: f81f8e6 + review fixes (follow-up commit)
- Scope: branch diff `main...HEAD` (brick B4, ADR-0009, spec `live-abstain`)
- Checks run: design · docs · tests · security · correctness
- Verdict: ship after the review fixes (applied) · Must 1 (fixed) · Should 4 (3 fixed, 1 disagree) · Nice 6

## Pre-merge gate (head SHA: review-fix commit)
| Step | Result |
|---|---|
| 1 Tests | ✅ 101 unit passed, 2 skipped (cv2 absent, pre-existing) · root `pytest` collection error is the known M1 issue (brick B3) |
| 2 Coverage | 88.5 % lines on the Sonar scope (`training/` excluded), 78 % including `training/` (main: 74 %) · changed files: use case 97 %, notifier 100 %, CLI 94 % · doc counter: not available in the project |
| 3 SonarQube | ⚠️ not run on the branch: Community Build analyses `main` only; run `make sonar` after merge |
| 4 Secrets | ✅ gitleaks `main..HEAD` clean · only `.env.example` tracked · diff read: nothing sensitive |
| 5 QA pass | ✅ CLI artefact: `--help` lists `--detector-floor`; `--detector-floor 0.7 --confidence 0.5` exits 2 with a clear error. Live run not possible (VespAI weights and cv2 not installed); wiring covered by `test_cli_wiring.py` |
- Gate: **GREEN for push**; merge after CI green and post-merge Sonar check.

## 🔴 Must Have
- `src/aristech/application/use_cases/detect_hornet_visual.py:17` `[design|correctness]` · `DetectionRun` kept every detection in lists; a camera stream never ends, and the floor makes abstentions frequent → unbounded memory · **Fixed**: counts (`threats: int`, `abstentions: int`).

## 🟡 Should Have
- `detect_hornet_visual.py:17` `[design]` · frozen dataclass with mutable lists · **Fixed** with the Must.
- `docs/architecture/traceability/matrix.md:7` `[docs]` · new `test_cli_wiring.py` missing · **Fixed**.
- `docs/architecture/specs/live-abstain.md:8` `[docs]` · present tense for the fixed bug · **Fixed**.

## 🔵 Nice to Have
- `tests/unit/interface/test_cli_wiring.py` `[tests]` · one test checks AC1/AC3/AC4/AC6 together; class-level `created` list (reset by fixture) · kept, acceptable at wiring level.
- `tests/unit/application/test_detect_hornet_visual.py` `[tests]` · edge cases `f == c`, `f == 0` · deferred to B3.
- `tests/unit/infrastructure/test_logging_notifier.py` `[tests]` · assert ACT log lacks "abstain" · deferred to B3.
- `docs/architecture/diagrams/detection/04-class.md` `[docs]` · `DetectionRun` not modelled (use cases are not in the class diagram) · kept.
- `src/aristech/interface/cli/main.py:111` `[design]` · `[0, 1]` check duplicates `DetectHornetVisualConfig` (pre-existing) · kept.

## ⚪ Disagree / Intentional
- `src/aristech/infrastructure/notify/logging_notifier.py:26` `[design]` · abstentions at INFO may be verbose · intentional: owner choice at the conception gate, recorded in ADR-0009 consequences.

## Per-dimension summary
- Design: dependency rule intact, port change justified (ADR-0009) · Docs: consistent, MCDA totals verified · Tests: AC1–AC6 covered with hand-written fakes · Security: none · Correctness: unbounded memory fixed.
