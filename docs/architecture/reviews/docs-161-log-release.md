# Local review — aristech (branch `docs/161-log-release`)

- Date: 2026-11-05
- Scope: `PROJECT_LOG.md` entries for PRs #162, #163, #166, #165 and the `v1.0.0-rc.1` release;
  `CHANGELOG.md` aligned with the tag; signing prerequisite in `docs/CONTRIBUTING.md`; this report
- Checks run: `just check` · adversarial review round 1 (2 Must, 3 Should, 2 Nice) ·
  verification round on the fix commit · SHAs `8f49338`, `a9065b9`, `c578cf5`, `6ada973`
  resolve; tag `v1.0.0-rc.1` points to `6ada973`, SSH signature verified on GitHub
- Verdict: ship once the verification round is clean

## Findings

| # | Priority | Finding | Resolution |
|---|---|---|---|
| 1 | Must | #166, #165 and the release (2026-11-05) sat under the `2026-11-02` heading | `## 2026-11-05` heading added |
| 2 | Must | `CHANGELOG.md` listed the #166 fix under `[Unreleased]` although the tag ships it, and dated rc.1 2026-11-02 | Fix moved into `[1.0.0-rc.1]`, dated 2026-11-05; the published release notes need the same edit (owner OK) |
| 3 | Should | #166 verification claimed `just gate`, its sources show `just check` | Reworded: `just check`, and `just gate` on the merged SHA (PR #165) |
| 4 | Should | #163 entry had no verification line | Added from the PR body |
| 5 | Should | This report predated the review | Rewritten with the rounds |
| 6 | Nice | Signing lesson only in the log | Prerequisite in CONTRIBUTING step 9 |
| 7 | Nice | QA row held the SHA checks | No runtime change: QA not applicable; checks moved above |

## Pre-merge gate

| Step | Result |
|---|---|
| 1 Tests | `just check` green (no code change) |
| 2 Coverage | no `src/` change |
| 3 SonarQube | `just gate` before merge |
| 4 Secrets | gitleaks in `just check`; diff read: no secret |
| 5 QA pass | not applicable: no runtime change |
