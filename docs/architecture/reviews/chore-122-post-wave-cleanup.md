# Pre-push review — chore/122-post-wave-cleanup

Review of the post-wave cleanup (issue #122) before the push.

- Date: 2026-10-30
- Scope: branch diff `origin/dev...HEAD` (`requirements.txt`, two workflows)
- Verdict: ship as-is · Must 0 · Should 0 · Nice 0

## Pre-merge gate

| Step | Result |
|---|---|
| 1 Tests | ✅ 270 unit on 3.11 and 3.12 · real weights: `make prefield-report` with pandas 2.3.3 reproduces `prefield-model-test-v1-tables.md` (ADR-0012) |
| 2 Coverage | tests 97.7 % (floor 80) |
| 3 SonarQube | ✅ PASSED (`just gate`) |
| 4 Secrets | ✅ gitleaks clean · diff read: versions and SHAs only |
| 5 QA pass | ✅ smoke: dependency and workflow pins |

## Content

- `requirements.txt`: pandas 2.2.2 → 2.3.3, pyyaml 6.0.1 → 6.0.3 (`uv pip compile -p 3.11`,
  pandas held below 3: a major needs its own ADR), replacing Dependabot #107.
- `codeql-action` v4.39.0 → v4.39.1 (SHA checked against the tag), replacing Dependabot #108,
  which still edited the removed `gitleaks.yml`.
- Closed in this brick: Dependabot #117 (frozen records, ADR-0026), issues #40 (ADR-0028) and #47
  (ADR-0010).

## 🔴 Must Have

_None._

## 🟡 Should Have

_None._

## 🔵 Nice to Have

_None._

## ⚪ Disagree / Intentional

- pandas 3.0 not taken · major version, out of scope.
