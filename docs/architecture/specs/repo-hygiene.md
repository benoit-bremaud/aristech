# Spec — repository hygiene (brick B6a)

> **Brick**: B6a · **Audit**: S9, S10, S11, S12, S14, S15 · **Decision**: ADR-0011 · **Out of
> scope**: S2 `docs/architecture.md` rewrite and English docs (B6b), S8 docstrings and issue #65
> (B6c), Dependabot relock (B7)

## Need

A contributor who reads the repository's tooling and meta files meets only things that work and
are true today: no dead documentation build, no duplicated licence, a lint command that matches
CI, a PR template that matches the attribution policy, an environment example that lists the
variables the code reads, and current pre-commit hooks.

## Acceptance criteria

- **AC1** `docs/source/`, `docs/Makefile`, `docs/make.bat`, the `docs` extra and `sphinx` in
  `requirements.in` are gone; `requirements.txt` is relocked without the Sphinx tree; no doc
  presents Sphinx as available (S9).
- **AC2** `docs/README.md` is a short English pointer to `docs/INDEX.md` (S9).
- **AC3** `docs/LICENSE.md` is deleted; no link points to it (S10).
- **AC4** `make lint` runs `ruff check` and `ruff format --check` on `src tests`; CONTRIBUTING gives
  `make lint type-check test` as the pre-push command and says what it covers (S11).
- **AC5** The PR template allows sober AI attribution (policy of 2026-07-02) (S12).
- **AC6** `.env.example` is in English and lists only variables read by `src/`, `scripts/` or
  `tests/` (dataset folders, `VESPAI_*`) (S14).
- **AC7** `.pre-commit-config.yaml` pins current hook releases and `pre-commit run -a` passes (S15).
- **AC8** `make lint type-check test-unit` is green.

## Design impact

No code structure change. Dropping the `docs` extra amends the extras list of ADR-0010 → ADR-0011.
No UML change.
