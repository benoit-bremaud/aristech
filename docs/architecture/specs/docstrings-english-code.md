# Spec — public docstrings and English code (brick B6c)

> **Brick**: B6c · **Audit**: S8, English rule · **Issue**: #65 · **Out of scope**: Dependabot
> relock (B7)

## Need

A reader of the code learns each public contract (port, domain rule, metric convention) from its
docstring, in English, without reading the implementation.

## Acceptance criteria

- **AC1** Public docstring coverage of `src/aristech` (modules, public classes, public functions and
  methods, measured by AST) is ≥ 90 % (S8). Docstrings state the contract or the *why*, never
  restate the signature.
- **AC2** The audit's named contracts are documented: the three ports, `Detection.is_hornet` vs
  `is_threat`, and the zero-division convention of `precision` / `recall` / `f1`.
- **AC3** `datasets/distribute.py` module docstring says "no environment access" instead of
  "no I/O"; `datasets/__init__.py` names the train/validation/test split (#65).
- **AC4** No French remains in `src/`, `tests/`, `scripts/`, `pyproject.toml`, `Makefile`,
  `config/` (comments, docstrings, CLI help, messages) (decision D2).
- **AC5** Behaviour unchanged: `make lint type-check test-unit` green, coverage not lower.

## Decisions (owner-validated 2026-10-16)

- **D1** docstring scope: whole public API + modules, ≥ 90 % (440) vs the audit list only (360) vs
  public + private (300). Criteria: global doc rule 35, reader value 25, no over-documentation 20,
  effort 20.
- **D2** include `scripts/` in the English pass (470) vs `src`, `tests`, project files only (360).
  Criteria: English rule 50, diff size 30, consistency 20.

## Design impact

Comments, docstrings and strings only; no code structure, UML or ADR change.
