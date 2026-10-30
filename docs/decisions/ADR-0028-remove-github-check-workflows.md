# ADR-0028: Remove the GitHub check workflows, keep the public security baseline

- Status: Accepted (owner, 2026-10-30)
- Date: 2026-10-30 (issue #110)
- Related: ADR-0025 (GitHub Actions on the signed tag only), ADR-0027 (local CI tiers), ADR-0007
  (security CI baseline, partly superseded: `gitleaks.yml` and `ci.yml` removed)

## Context

ADR-0027 put every check of `ci.yml` (ruff, mypy, pytest) and `gitleaks.yml` in `just check`, run by
the pre-push hook, with more checks than CI held (typos, zizmor, Semgrep, osv-scanner, coverage
floor). The cross-project decision of 2026-10-30 (benoit-bremaud/agents-skills#259) keeps
`codeql.yml`, `scorecard.yml` and `dependency-review.yml` on public repositories. What `ci.yml` still
added: the Python 3.12 test run, and a net under a push made with `--no-verify`.

## Options (MCDA)

Script: [`mcda/adr_0028_remove_check_workflows.py`](mcda/adr_0028_remove_check_workflows.py).

| Option | ADR-0025 conformance 30 | Safety net 25 | Simplicity 20 | One toolchain 15 | Cost, time 10 | Total |
|---|---|---|---|---|---|---|
| A. Remove `ci.yml` | 5 | 1 | 5 | 5 | 5 | **400** |
| B. Reduce it to mise-action → `just check` | 2 | 4 | 3 | 5 | 3 | 325 |
| C. Keep it as is | 1 | 3 | 2 | 1 | 3 | 190 |

Sensitivity: safety net 45 → B 360, A 320; conformance 40 → A 440. B wins only if a bypassed hook
is a real risk: the owner is the only one pushing, the `protect-dev` ruleset requires a pull
request, and `just gate` runs before every merge.

## Decision

- Remove `.github/workflows/ci.yml` and `.github/workflows/gitleaks.yml`.
- Keep `codeql.yml`, `scorecard.yml` and `dependency-review.yml` (public-repository baseline).
- `just gate` also runs the unit tests on Python 3.12 (`just test-312`, throwaway uv environment),
  so both supported versions stay covered.
- Merge rule: `just gate` green on the head SHA, GitHub security checks green, every comment
  handled (`CONTRIBUTING.md` step 5, PR template, `CLAUDE.md`).

## Consequences

- No GitHub status check runs ruff, mypy or the tests; a pull request shows CodeQL and dependency
  review only. Nothing proves on GitHub that `just gate` ran until the cross-project attestation
  (`gate` commit status, ADR-0025) lands.
- Historical records that mention `ci.yml` (ADR-0007, older gates and reviews, `PROJECT_LOG.md`)
  stay as written.
