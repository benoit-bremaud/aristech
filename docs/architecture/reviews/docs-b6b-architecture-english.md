# Pre-push review — docs/b6b-architecture-english (brick B6b)

- Date: 2026-10-16 · Base: `main` `997f705` · Spec: `specs/docs-freshness-english.md`
- Scope: Markdown documentation only; no code change.

## Execution checks

| Check | Result |
|---|---|
| `make lint type-check test-unit` | ✅ 107 passed |
| `pre-commit run -a` | ✅ |
| `markdownlint` on rewritten files | ✅ |
| Relative link check over touched files | ✅ (one `path.md` hit is an example inside a code span) |
| `gitleaks detect` | ✅ no leaks |
| French grep outside `docs/research/` | ✅ none in touched files |

## Acceptance criteria

| AC | Evidence |
|---|---|
| AC1 | `docs/architecture.md` rewritten (layers, 3 ports + adapters, `decide()`, evaluation, datasets, runtime flow, tests, legal floor, open decisions) |
| AC2 | No `Target` / `NeutralizeTarget` / speculative port left in ROADMAP, requirements, architecture |
| AC3 | `BOM.md`, `DIY_INSTRUCTIONS.md` deleted; INDEX row to `prototype-foundations.md` § B, § C |
| AC4 | README, CONTRIBUTING, INSTALL, MAINTENANCE, `models/README.md`, `tests/e2e/README.md`, requirements in English |
| AC5 | `docs/research/` untouched: its French is citations only |
| AC6 | link check |

## Findings

- **Must**: none.
- **Should** (fixed while translating): README claimed "8 ports", "adapters empty", a "private"
  repository and a `portaudio` prerequisite; INSTALL listed solar/sonar/LoRaWAN settings and no
  `vision` extra; CONTRIBUTING still named Copilot/Codex as reviewers and the `DetectHornetAudio`
  example; requirements still held "UML diagrams held" and the BOM/DIY reconciliation item. All
  aligned with the as-built state.
- **Nice** (deferred to B6c): `pyproject.toml`, `Makefile`, `config/config.yaml`, CLI help strings
  and code comments are still French.
