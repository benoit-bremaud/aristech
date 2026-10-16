# Pre-push review — docs/b6c-docstrings-english (brick B6c)

- Date: 2026-10-16 · Base: `main` `76362f9` · Spec: `specs/docstrings-english-code.md`
- Scope: docstrings, comments, CLI help and log strings, project files; no logic change.

## Execution checks

| Check | Result |
|---|---|
| `make lint type-check` | ✅ |
| `pytest --cov` (default selection) | ✅ 109 passed, coverage 96 % (unchanged) |
| `pre-commit run -a` | ✅ |
| `gitleaks detect` | ✅ no leaks |
| Public docstring coverage (AST: modules, public classes, functions, methods) | ✅ 84/84 = 100 % (was 35/84 = 41.7 %) |
| French grep over `src tests scripts pyproject.toml Makefile config` | ✅ none |
| QA smoke: `python -m aristech`, `aristech --help` | ✅ English output, exit 0 |

## Acceptance criteria

| AC | Evidence |
|---|---|
| AC1 | 100 % public docstrings; each states a contract or a reason |
| AC2 | ports documented; `is_hornet` vs `is_threat`; `ClassMetrics` zero-division convention (0.0, never NaN) |
| AC3 | `datasets/distribute.py` "no environment access"; `datasets/__init__.py` names the split (#65) |
| AC4 | grep above |
| AC5 | suite and coverage unchanged |

## Findings

- **Must**: none.
- **Should** (fixed): `config/config.yaml` still carried the 2024 sections (sound detection, coil
  gun GPIO, solar, sonar, LoRaWAN) that no code reads; reduced to the `app` section the CLI reads,
  and `test_config_loading` asserts that instead of the dead sections.
  `scripts/measure_operating_point.py` told the user to set `hornet_detection.confidence_threshold`
  in the config, which nothing reads; it now points to `--confidence`.
- **Nice** (pre-existing, not in scope): the default `logging.yaml` file handler fails when
  `logs/` does not exist, so the CLI falls back to `basicConfig` with a warning.
