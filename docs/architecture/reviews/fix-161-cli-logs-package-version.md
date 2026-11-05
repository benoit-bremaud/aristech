# Pre-push review — fix/161-cli-logs-package-version

Review of the diff against `dev` (issue #161) before the first push: the CLI start-up line logs
`aristech.__version__` instead of `app.version` copied into `config/config.yaml` (hosted review
finding on the promotion PR #165).

## Checks

- `just check`: green (366 tests, coverage 98 %).
- Adversarial review (fresh agent, round 1): 0 Must, 2 Should, 3 Nice; gate open. Verification
  round on the fix commit: see the table.

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
