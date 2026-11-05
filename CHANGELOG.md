# Changelog

Notable changes to aristech, in the [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)
format; versions follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

The Git tag carries the SemVer form (`v1.0.0-rc.1`); `pyproject.toml` carries the PEP 440 form of
the same version (`1.0.0rc1`).

## [Unreleased]

## [1.0.0-rc.1] - 2026-11-05

First release candidate of v1, "detection + alert" (Epic #19). Stable `1.0.0` follows once the
candidate passes a test on a real Telegram bot and the QA pass on the bench Raspberry Pi 5.

### Added

- Evaluation harness and dataset tooling: offline metrics per class, manifest and split helpers
  (#17).
- Operating point for the ACT decision: threshold 0.45 with abstention (ADR-0029, #18).
- Live detection with the RF-DETR detector at the ACT threshold (ADR-0030, #140).
- COUNT point and one attack alert per episode (ADR-0031, #149).
- Attack alert pushed on a Telegram channel through a delayed queue (ADR-0032, #152).
- Daily heartbeat and fault pushes (`loop_error`, `source_ended`), one per fault kind per hour
  (ADR-0033, #158).
- Capture rig design for the bench unit: microphone end-of-life check and bench order list
  (ADR-0017, #84, #132).

### Changed

- Python 3.11 is the minimum version; vulnerable vision pins bumped (#111).
- Branching model: `dev` integration branch, field-ready `main`, signed `v*` tags (ADR-0025).
- Local CI tiers `just fast`, `just check` and `just gate` replace the GitHub check workflows
  (ADR-0027).

### Fixed

- The CLI creates the `logs/` folder before the file handler opens it (#143).
- The start-up log line reports the package version; `app` section removed from
  `config/config.yaml` (#161).

### Known limits

- The VespAI detector does not transfer to the target apiary; RF-DETR Small replaces it
  (velutina precision 0.57, recall 0.48 on test-v1).
- The heartbeat ticks per processed frame: a hung unit sends none, so the beekeeper is the
  dead man's switch until the server watchdog (M6).
- The fault rate limit is per process.

[Unreleased]: https://github.com/benoit-bremaud/aristech/compare/v1.0.0-rc.1...HEAD
[1.0.0-rc.1]: https://github.com/benoit-bremaud/aristech/releases/tag/v1.0.0-rc.1
