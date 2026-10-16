# Local review — aristech (branch diff main...ci/security-baseline)

- Date: 2026-10-16
- Commit: f533fd8
- Scope: branch diff `main...HEAD` — 5 YAML files (`.github/workflows/{gitleaks,codeql,dependency-review,scorecard}.yml`, `.github/dependabot.yml`)
- Checks run: security · correctness (design · docs · tests not applicable: no source code in the diff)
- Verdict: ship as-is · Must 0 · Should 1 · Nice 1

## 🔴 Must Have
_None._

## 🟡 Should Have
- repo settings `[security]` · Dependabot security updates, secret scanning and push protection were disabled although free on a public repo · enabled via the GitHub API (owner-approved 2026-10-16).

## 🔵 Nice to Have
- `.github/workflows/gitleaks.yml:29` `[correctness]` · on pull requests from forks the token lacks `security-events: write`, so the SARIF upload step fails · guard with `github.event.pull_request.head.repo.full_name == github.repository`; tracked as a backlog issue.

## ⚪ Disagree / Intentional
- `.github/workflows/dependency-review.yml:16` `[security]` · `fail-on-severity: high` (not `low`) · keeps PRs unblocked by low/moderate advisories; Dependabot surfaces those.

## Per-dimension summary
- Design: n/a (CI config only) · Docs: n/a · Tests: n/a · Security: all actions SHA-pinned, least-privilege job permissions, `actionlint` clean, local gitleaks full-history clean · Correctness: CodeQL default setup not configured, so no conflict with the advanced workflow.
