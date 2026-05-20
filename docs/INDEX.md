# Documentation Index

Entry point to every document in this repository. Each entry has its
role in one line so a new reader can pick the right doc without
opening five of them.

## Project-level (root)

| Document                                    | Role                                                                                                                |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [README.md](../README.md)                   | Top-level project pitch and quick-start.                                                                            |
| [PROJECT_LOG.md](../PROJECT_LOG.md)         | Chronological operational logbook — one entry per merged PR, tag, or significant decision. Authority on _when / why_. |
| [LICENSE](../LICENSE)                       | MIT.                                                                                                                |
| [pyproject.toml](../pyproject.toml)         | Packaging and tooling configuration (PEP 621).                                                                       |
| [Makefile](../Makefile)                     | Common dev commands (`make test-unit`, `make lock`, etc.).                                                            |
| [.pre-commit-config.yaml](../.pre-commit-config.yaml) | pre-commit hooks (ruff, mypy).                                                                                 |
| [.markdownlint.json](../.markdownlint.json) | Markdown linting config — `MD013`, `MD033`, `MD041`, `MD060` disabled for stylistic reasons.                          |

## Architecture and design

| Document                                                  | Role                                                                                                                                                  |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| [docs/architecture.md](architecture.md)                   | Clean Architecture layers, ports, use cases, open decisions, hard constraints (legal floor). Authority on _how aristech models the world_.            |
| [docs/usage.md](usage.md)                                 | High-level usage notes.                                                                                                                                |
| [docs/source/](source/)                                   | Sphinx documentation source (HTML build under `_build/`).                                                                                              |
| [docs/Makefile](Makefile) / [docs/make.bat](make.bat)     | Sphinx build entry points.                                                                                                                             |

## Operational (install, maintenance, governance)

| Document                                                       | Role                                                                                              |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| [docs/INSTALL.md](INSTALL.md)                                  | Installation instructions for the codebase.                                                       |
| [docs/MAINTENANCE.md](MAINTENANCE.md)                          | Post-merge hygiene, `git filter-repo` procedure, lock regeneration.                                |
| [docs/CONTRIBUTING.md](CONTRIBUTING.md)                        | Contribution rules (PR workflow, conventions).                                                     |
| [docs/LICENSE.md](LICENSE.md)                                  | License notes complementing root `LICENSE`.                                                        |

## Hardware / DIY

| Document                                                       | Role                                                                                              |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| [docs/DIY_INSTRUCTIONS.md](DIY_INSTRUCTIONS.md)                | DIY build instructions for the apiarist (legacy — to be revised against `docs/research/prototype-foundations.md`). |
| [docs/BOM.md](BOM.md)                                          | Bill of Materials (legacy — to be revised against the new BOM section in `prototype-foundations.md` § C). |

## Research

The research subdirectory follows a tri-document discipline:
**SOTA narrative + applied engineering inputs + centralised bibliography.**
See skill `aristech-research-navigation` (in `~/.claude/skills/`) for
the full authoring rules.

| Document                                                                 | Role                                                                                                                                                      |
| ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [docs/research/state-of-the-art.md](research/state-of-the-art.md)        | **Literature / prior-art survey** — Kaggle, GitHub, academic papers, HuggingFace, auto-aim turret prior art, EU/FR legal framework. Authority on _what's been done_. |
| [docs/research/prototype-foundations.md](research/prototype-foundations.md) | **Applied engineering inputs** — behavioural biology at the hive entrance, Éric Darrouzet synthesis, hive geometry and sensor mounting, hardware BOM and energy autonomy. Authority on _what aristech will build with_. |
| [docs/research/references.md](research/references.md)                    | **Centralised bibliography** — every URL cited in the survey + foundations docs, grouped by domain. Authority on _where the citations live_.              |

## Reports (early planning artefacts)

| Document                                                                  | Role                                                                |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| [docs/reports/initial_analysis.pdf](reports/initial_analysis.pdf)         | Early project analysis (placeholder — empty file pending content).   |
| [docs/reports/requirement_specification.pdf](reports/requirement_specification.pdf) | Requirement specification (placeholder — empty file pending content). |

## How to choose where to write new content

| Kind of new content                                                  | Goes in                                                                                          |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| A merged PR's chronological entry                                    | `PROJECT_LOG.md`                                                                                  |
| A formal architectural decision (was deferred → tranché)              | `docs/architecture.md` + a `Decisions:` sub-bullet under the PR entry in `PROJECT_LOG.md`        |
| A new academic paper / dataset / repo discovered                     | `docs/research/state-of-the-art.md` (narrative) + `docs/research/references.md` (URL index)      |
| A new vendor link or BOM line item                                   | `docs/research/prototype-foundations.md` § C + `docs/research/references.md` § 16                |
| A measured biological constant                                        | `docs/research/prototype-foundations.md` § A (flag `peer-reviewed` / `unverified` / `aristech-measured`) |
| A new FR/EU legal text                                               | `docs/research/state-of-the-art.md` § Legal framework + `docs/research/references.md` § 10 / 11 |
| A new top-level doc                                                   | Add a row to this `docs/INDEX.md` and to the `aristech-research-navigation` skill if applicable. |

## Maintenance

- This index is the **map**, not the content. Lines stay one-per-doc with a single-sentence role.
- Update this file every time a top-level doc is added, renamed, removed, or its role changes.
- The companion skill `aristech-research-navigation` (`~/.claude/skills/aristech-research-navigation/SKILL.md`) carries the **authoring rules** (where to put new content, cross-link discipline, honesty markers). This index carries only the **map**.
