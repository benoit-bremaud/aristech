# Pre-push review — chore/b6a-repo-hygiene (brick B6a)

- Date: 2026-10-16 · Base: `main` `793b503` · Spec: `specs/repo-hygiene.md` · ADR-0011
- Scope: tooling and meta files only; no `src/` or `tests/` change.

## Execution checks

| Check | Result |
|---|---|
| `make lint` (now `ruff check` + `ruff format --check`) | ✅ |
| `make type-check` | ✅ 31 files |
| `make test-unit` | ✅ 107 passed |
| `pre-commit run -a` with updated hooks | ✅ |
| `gitleaks detect` | ✅ no leaks |
| Coverage / Sonar | Unchanged code; post-merge `make sonar` |
| QA smoke | N/A: no runtime change |

## Acceptance criteria

| AC | Evidence |
|---|---|
| AC1 | `docs/source`, `docs/Makefile`, `docs/make.bat` deleted; `docs` extra and `sphinx` removed; `requirements.txt` relock is removals only (Sphinx tree, `requests`, `certifi`, `idna`, `pygments`, `urllib3`) |
| AC2 | `docs/README.md` points to `INDEX.md` |
| AC3 | `docs/LICENSE.md` deleted; INDEX row removed |
| AC4 | `Makefile` `lint` target; CONTRIBUTING note |
| AC5 | PR template checklist line |
| AC6 | `.env.example` lists the 8 dataset folders and 3 `VESPAI_*` variables, all read in code |
| AC7 | hooks v6.0.0 / ruff v0.17.1 / mypy v2.4.0 |
| AC8 | see execution checks |

## Findings

- **Must**: none.
- **Should** (fixed): the ruff hooks linted `scripts/` and empty notebooks that CI never checks;
  scoped to `^(src|tests)/` to match CI. The trailing-whitespace hook fixed one blank line in
  `scripts/prepare_directories.py`, kept.
- **Nice** (deferred to B6b): CONTRIBUTING and INSTALL stay French until the English pass.
