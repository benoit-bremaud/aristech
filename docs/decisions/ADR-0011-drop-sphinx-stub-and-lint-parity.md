# ADR-0011: Drop the Sphinx stub and align `make lint` with CI

- Status: Accepted
- Date: 2026-10-16 (brick B6a, owner-validated weights and options)
- Amends: the tooling extras left by ADR-0010 (removes `docs`)

## Context

The audit found a Sphinx stub generated in 2024 (`docs/source`, `docs/Makefile`, `docs/make.bat`,
a `docs` extra, `sphinx` in `requirements.in`) that builds nothing useful and that `docs/INDEX.md`
presents as functional (S9). It also found that `make lint` skips `ruff format --check`, which CI
runs, so a green local lint can still fail CI (S11). Spec: `docs/architecture/specs/repo-hygiene.md`.

## Decision 1 — fate of the Sphinx stub

Criteria and weights: YAGNI 35, documentation truth 25, dependency / CVE surface 20,
reintroduction cost 20.

| Option | C1 | C2 | C3 | C4 | Total /500 |
|---|---|---|---|---|---|
| A. Delete the stub, the extra and `sphinx` from the lock | 5 | 5 | 5 | 4 | **475** |
| B. Make Sphinx work (autodoc + CI build) | 2 | 5 | 1 | 5 | 300 |
| C. Keep it, mark it unused | 3 | 3 | 2 | 5 | 320 |

No reader consumes HTML docs today; the Markdown dossier is the documentation. **Chosen: A.**

## Decision 2 — lint parity with CI

Criteria and weights: local/CI parity 50, simplicity 25, fixes the root cause 25.

| Option | C1 | C2 | C3 | Total /500 |
|---|---|---|---|---|
| A. `make lint` also runs `ruff format --check`; CONTRIBUTING updated | 5 | 5 | 5 | **500** |
| B. Fix only the CONTRIBUTING command | 2 | 5 | 1 | 250 |

**Chosen: A.**

## Consequences

- Tooling extras are `dev` and `gpu`; an API reference comes back with a real reader, through a
  new ADR.
- Dropping Sphinx from the lock removes its transitive packages (e.g. `jinja2`, `Pygments`).
- `make lint` fails on unformatted code; `make format` fixes it.
