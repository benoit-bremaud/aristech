# Local review — aristech (issue #161, CLI logs the package version)

- Date: 2026-11-05
- Scope: branch diff `dev...fix/161-cli-logs-package-version` — the start-up line logs
  `aristech.__version__` instead of `app.version` copied into `config/config.yaml` (hosted
  review finding on the promotion PR #165)
- Checks run: `just check` (366 tests, coverage 98 %) · adversarial review round 1 (0 Must,
  2 Should, 3 Nice) · verification round on `407d202`: 5/5 fixed, 0 regressed
- Verdict: ship · Must 0 · Should 2 (fixed) · Nice 3 (fixed)

## Findings

| # | Priority | Finding | Resolution |
|---|---|---|---|
| 1 | Should | The new version test passed only by test order: `test_creates_missing_log_folder` loads a logging config without `disable_existing_loggers`, which disables the `aristech` logger | Fixture mirrors `config/logging.yaml` (`disable_existing_loggers: false`) |
| 2 | Should | `app.name` was dead config (no reader) | Whole `app` section dropped; the config test asserts the exact section set |
| 3 | Nice | Six wiring fixtures still wrote the removed `app.version` key | Removed |
| 4 | Nice | `pyproject.toml` and `__version__` are two copies with no check | Test `test_package_version_matches_pyproject` |
| 5 | Nice | `CHANGELOG.md` `[Unreleased]` empty | `Fixed` entry added |
| 6 | Disagree | Module-level `from aristech import __version__` in the interface layer | Allowed: the package root holds only `__version__`; the dependency rule restricts `domain/` and `application/` |

No QA pass on a running product beyond the CLI tests: the diff changes one log line and one
config key.
