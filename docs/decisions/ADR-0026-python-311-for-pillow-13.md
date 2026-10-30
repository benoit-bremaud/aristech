# ADR-0026: Python ≥ 3.11 so the `vision` extra can take Pillow 13

- Status: Accepted (owner, 2026-10-30)
- Date: 2026-10-30 (issue #111)
- Amends: the supported Python versions of ADR-0001 and the Pillow bound of ADR-0012 (version
  bounds only)

## Context

osv-scanner, measured for the local CI (#109), flags four packages in `requirements.txt`, the lock
of the `vision` extra: pillow 12.3.0 (41 advisories, highest severity 9.8), filelock 4.1.0,
setuptools 84.0.0, and, in the frozen M3 environment record only, certifi. Every Pillow advisory is
fixed in **Pillow 13.0.0 and nothing earlier** (PyPI: no 12.3.x patch release).

Checked 2026-10-30:

- Pillow 13.0.0 declares `Requires-Python >=3.11`. With `requires-python = ">=3.10"`, a lock
  compiled for 3.10 and the `Pillow<13` cap of ADR-0012, the resolver refuses.
- **Python 3.10 reached end of life on 2026-10-01** (PEP 619, endoflife.date): no more security
  releases.
- The field device runs Raspberry Pi OS Bookworm or later (`INSTALL.md`), whose system Python is
  3.11 or later; aristech uses it with `--system-site-packages` for Picamera2, so the device never
  ran 3.10. The development and training machine has 3.11 and 3.12 through uv.
- aristech code never imports PIL; torchvision, yolov5 and rfdetr do.

## Options (MCDA)

Script: [`mcda/adr_0026_python_311_pillow_13.py`](mcda/adr_0026_python_311_pillow_13.py). Scores
0–5, weights /100, totals /500; scores are estimates until the real-weights run below.

| Option | Closes the vulnerabilities 35 | Runtime risk 25 | Scope, effort 15 | Simplicity 15 | Python support breadth 10 | Total |
|---|---|---|---|---|---|---|
| A. Python ≥ 3.11 + Pillow 13 | 5 | 4 | 2 | 5 | 4 | **420** |
| B. Markers: Pillow 13 on ≥ 3.11, 12.3 on 3.10 | 3 | 3 | 3 | 1 | 5 | 290 |
| C. Keep Pillow 12.3 under a time-boxed waiver, fix the other three | 2 | 5 | 5 | 4 | 5 | 380 |

Sensitivity: effort 35 and vulnerabilities 15 → **C 440**, A 360; vulnerabilities 50 → A 440,
C 340. C wins only if effort outweighs security. B keeps the 3.10 path vulnerable and doubles the
environments. A drops a version that is already end-of-life, so its breadth cost is low.

## Decision

- `requires-python = ">=3.11"`; classifiers 3.11 and 3.12; ruff `target-version = "py311"`;
  mypy `python_version = "3.11"`; SonarQube `sonar.python.version=3.11`.
- `vision` extra: `Pillow>=13.0,<14`; `requirements.in` floors `Pillow>=13.0`, `filelock>=4.2.1`.
- `requirements.txt` is locked for Python 3.11, the lowest supported version, by
  `uv pip compile -p 3.11` (`make lock`, which used to call pip-compile while the lock header
  already said uv).
- CI lint on 3.11, tests on 3.11 and 3.12.
- The `py311` target turns on two pyupgrade rules, applied in the same change: `timezone.utc` →
  `datetime.UTC`, and `(str, Enum)` → `StrEnum` for `Species`, `Split` and `Decision`. `StrEnum`
  changes only `str()` and `format()` of a member; no code calls either on these enums.

## Consequences

- Development venvs move to 3.11 (`CLAUDE.md`, `INSTALL.md`); the training venv is rebuilt on 3.11.
- Real-weights check (as in ADR-0012): `make prefield-report` on a fresh 3.11 venv with the new
  lock must reproduce `docs/research/prefield-model-test-v1-tables.md`; recorded in the pull request.
- The frozen environment records (`docs/research/m3-vespai-baseline-requirements.txt`,
  `prefield-model-environment.txt`) describe past runs and stay as they are; #109 excludes them
  from the osv-scanner scan.
- numpy 2 and opencv-python 5 stay held back (ADR-0012), unchanged.
