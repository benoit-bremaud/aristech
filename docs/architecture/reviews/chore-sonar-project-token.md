# Pre-push review — `chore/sonar-project-token`

Scope: `Makefile` (`sonar` target reads the project token file), `CLAUDE.md` (Quality paragraph).

## Checks

- `make lint`, `make type-check`, `make test-unit` (94 passed, 2 skipped: no `cv2`), `ruff format --check src tests`: green.
- Control scan `make sonar` with the project token `project-aristech-local-2026` read from
  `~/.config/sonar-tokens/aristech`: ANALYSIS SUCCESSFUL, report uploaded.

## Findings

| # | Severity | Finding | Verdict |
|---|----------|---------|---------|
| 1 | — | Token value never echoed: read from a `umask 077` file via command substitution, not printed by `make` (the recipe line shows the `cat` expression, not the value). | OK |
| 2 | — | Fallback to `SONAR_TOKEN` keeps the global-token path working when the file is absent. | OK |
| 3 | Nice | The project is public on the local server; a project analysis token cannot read results, so reading the gate needs a user token (MCP config). Out of scope. | Noted |

No Must / Should findings.
