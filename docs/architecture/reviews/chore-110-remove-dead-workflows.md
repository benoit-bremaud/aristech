# Pre-push review — chore/110-remove-dead-workflows

Review of the removal of the GitHub check workflows (ADR-0028, issue #110) before the push.

- Date: 2026-10-30
- Scope: branch diff `origin/dev...HEAD`
- Checks run: design · docs · security · correctness (diff read in full)
- Verdict: ship as-is · Must 0 · Should 0 · Nice 1

## Pre-merge gate

| Step | Result |
|---|---|
| 1 Tests | ✅ 270 unit on 3.11 and 270 on 3.12 (`just test-312`) · wiring test OK |
| 2 Coverage | tests 97.7 % (floor 80) |
| 3 SonarQube | ✅ PASSED (`just gate`, 53 s) |
| 4 Secrets | ✅ gitleaks full history clean · diff read: nothing sensitive |
| 5 QA pass | ✅ smoke: tooling and docs only |

## 🔴 Must Have

_None._

## 🟡 Should Have

_None._

## 🔵 Nice to Have

- `.github/workflows/` `[security]` · no GitHub check proves `just gate` ran · the `gate` commit
  status of the cross-project attestation tooling (ADR-0025) closes it.

## ⚪ Disagree / Intentional

- ADR-0007, older gates and reviews still name `ci.yml` · historical records, kept as written
  (ADR-0028 § Consequences).
