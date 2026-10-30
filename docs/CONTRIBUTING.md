# Development workflow

Internal workflow notes for aristech, an R&D project. This document describes the conventions
applied from commit to merge; it is the reference for the maintainer and for any collaborator who
joins later.

## Dev install

```bash
git clone git@github.com:benoit-bremaud/aristech.git
cd aristech
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Method

aristech follows a design-first method (ADR-0008):

- **Design dossier first** — model a feature in [docs/architecture/](architecture/README.md)
  (spec, UML) and get the conception gate signed before writing implementation code.
- **ADRs** — every structuring decision goes in [docs/decisions/](decisions/README.md) with scored
  options; an accepted ADR is superseded, never edited.
- **Review report** — every branch gets a pre-push review report in
  `docs/architecture/reviews/<branch>.md`.

## Branch conventions

Two long-lived branches (ADR-0025, flow in
[`architecture/diagrams/promotion/01-activity.md`](architecture/diagrams/promotion/01-activity.md)):

- `dev` — integration. Always green; every work branch starts here and comes back here by a
  squash-merged pull request.
- `main` — field-ready. Every commit is installable on a device at the apiary. It receives only
  **merge-commit** pull requests from `dev`, for a commit that passed QA on staging (the bench
  device; `just gate` locally until it exists), and hotfixes.

`dev` is the GitHub default branch. Never commit directly to `main` or `dev`. Always branch from
`dev`; a **hotfix** branches from `main`, goes through the same gate and QA, and `main` is merged
back into `dev` right after by a merge-commit pull request.
Staging is an environment, not a branch. A signed tag `vX.Y.Z` on `main` marks the production
version and is the only trigger of GitHub Actions.

| Prefix             | For                                            |
| ------------------ | ---------------------------------------------- |
| `feat/<topic>`     | new feature                                    |
| `fix/<topic>`      | bug fix                                        |
| `docs/<topic>`     | documentation only                             |
| `research/<topic>` | technical survey, new study                    |
| `refactor/<topic>` | restructuring without behaviour change         |
| `chore/<topic>`    | repository hygiene                             |
| `ci/<topic>`       | CI workflow change                             |

## Work cycle

1. Create the dedicated branch from `dev` (from `main` for a hotfix).
2. Develop, then run locally:

   ```bash
   make lint type-check test
   ```

   `make lint` runs `ruff check` and `ruff format --check`, like CI; `make format` fixes the
   formatting.

3. Commit in [Conventional Commits](https://www.conventionalcommits.org/) format:

   ```text
   feat(application): report abstentions through the notifier
   fix(infrastructure): close OpenCV VideoCapture on exception
   docs(research): add Hall et al. 2025 to acoustic section
   ```

4. Open a pull request to `dev`. The template (`.github/PULL_REQUEST_TEMPLATE.md`) applies
   automatically; fill every section.
5. Merge gate: CI green (ruff, mypy, pytest 3.11–3.12, security baseline), every review comment
   handled, local checks green (tests, lint, format, mypy, coverage, gitleaks, smoke run).
6. Squash-merge into `dev` and delete the branch, then clean up locally:

   ```bash
   git checkout dev && git pull
   git branch -d <branch>   # -D if needed: a squash merge often leaves the branch "unmerged" for git
   git remote prune origin
   ```

7. Add the `PROJECT_LOG.md` entry for the merged PR.
8. Promotion to `main`: once the `dev` commit has passed QA on staging, open a pull request
   `dev` → `main` and merge it with a **merge commit** (never a squash: the attested SHA must
   reach `main`). The owner then cuts the signed tag when a field version is wanted.

## Code standards

### Python

- **mypy strict** passes on `src/` (except explicit overrides in `pyproject.toml` for
  `infrastructure/`).
- **No unjustified `Any`.** If one is needed, comment why.
- **Explicit named exports** through `__all__`.
- **Clean Architecture** ([architecture.md](architecture.md)): `domain` depends on nothing;
  `application/ports` are `Protocol`s; concrete implementations live in `infrastructure/`; heavy
  libraries go in an optional extra.

### Style

- **ruff** for lint and format (`pyproject.toml`). Run `make format lint` before committing.
- **No obvious comments**: a comment explains a non-trivial *why*, never a *what* the code shows.
- **Docstrings** short and factual on ports, use cases and public functions.

### Tests

- **Tests are mandatory** for every new feature or bug fix.
- **Levels**:

  | Level                | Scope                                                     | pytest marker  |
  | -------------------- | --------------------------------------------------------- | -------------- |
  | `tests/unit/`        | domain, use cases with fakes at the ports, evaluation     | none           |
  | `tests/integration/` | real adapters; needs `.env`, weights or data              | `integration`  |
  | `tests/e2e/`         | end to end, may need hardware                             | `e2e`          |

- **Fakes over mocks**: implement the target `Protocol` in a class local to the test. More
  readable, type-safe; never mock the domain.

## Security

- **Never put secrets** in code, commits or examples. `.env.example` holds placeholders only.
- **No force-push to `main` or `dev`.**
- **aristech legal floor** (Code de l'environnement L411-1 + L415-3): any feature that could harm a
  pollinator defaults to abstention. See [architecture.md § Legal floor](architecture.md#legal-floor).

## Documentation discipline

See [docs/INDEX.md](INDEX.md) for the document map. Rules:

- All artefacts in English.
- No Obsidian `[[wikilinks]]`; standard Markdown links `[text](path.md)` only.
- Every URL cited in a narrative also goes in
  [docs/research/references.md](research/references.md).
- Structuring decisions go in an ADR; the `PROJECT_LOG.md` entry of the PR summarises them.
- `markdownlint` passes (`npx markdownlint-cli <file>`) before committing.

## Tracking

Tasks and PRs are tracked in the GitHub Project **aristech #57**. Bugs and feature ideas are
issues attached to it, labelled by the Clean Architecture layer they touch (`domain` /
`application` / `infrastructure` / `interface`).
