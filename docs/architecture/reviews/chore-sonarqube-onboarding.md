# Local review — aristech (branch diff main...chore/sonarqube-onboarding)

- Date: 2026-10-16
- Commit: a16d5f5
- Scope: branch diff `main...HEAD` — `sonar-project.properties`, `Makefile`, `.gitignore`
- Checks run: security · correctness · execution (`make sonar` run end to end) (design · docs ·
  tests not applicable: configuration only)
- Verdict: ship as-is · Must 0 · Should 1 · Nice 1

## 🔴 Must Have

_None._

## 🟡 Should Have

- `CLAUDE.md` `[docs]` · the `make sonar` command and the `SONAR_TOKEN` requirement are not yet
  documented in the project rules · add one line to `CLAUDE.md` once PR #49 (which creates it)
  is merged.

## 🔵 Nice to Have

- `Makefile:34` `[correctness]` · `SONAR_TOKEN` exported from `~/.zshrc` is only visible to
  interactive shells, so non-interactive runs fail with HTTP 401 · export it from `~/.zshenv`
  (machine setup, not repo).

## ⚪ Disagree / Intentional

- `sonar-project.properties:7` `[security]` · `sonar.host.url` hard-codes `localhost:9000` · the
  shared Community Build is local by design; no secret in the file, the token comes from the
  environment.
- `sonar-project.properties:16` `[correctness]` · `training/` excluded · legacy package slated for
  removal (audit S3).

## Execution evidence

- `make sonar`: 94 passed, 2 skipped; `ANALYSIS SUCCESSFUL`.
- Quality gate OK; coverage 84.3 %; bugs 0; vulnerabilities 0; hotspots 0; duplication 0 %;
  code smells 2 (S7517, issue #50, deferred to B3).

## Per-dimension summary

- Security: no secret, token from environment · Correctness: target verified end to end.
