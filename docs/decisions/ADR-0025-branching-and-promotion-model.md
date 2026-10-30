# ADR-0025: `dev` integration branch, field-ready `main`, staging as an environment, signed tags

- Status: Accepted (owner, 2026-10-30)
- Date: 2026-10-30 (issue #112; prerequisite of #111, #109 and #110)

## Context

aristech is moving to a local-first CI/CD: deterministic checks on the developer machine
(`just check` before every push, `just gate` before every merge), GitHub Actions kept for the
production deploy only (cross-project epic benoit-bremaud/agents-skills#210, wave 0 bis #259).
Before the local tiers are built (#109) and the GitHub workflows removed (#110), the project needs
to fix **which branches exist and how a change is promoted** to the field.

The owner's needs, collected on 2026-10-30:

1. Any commit of `main` must be **ready for the field**: installable on a device in front of a hive.
2. Production is three things: the device at the apiary, the published model (weights + report on
   the frozen test set), later a service or an app. Today the device is being built
   (ADR-0017), so production is marked by the signed tag only.
3. Staging is **QA**: the product as in production, without end users. When QA passes, the
   change goes to production.
4. An **integration branch** where several contributors converge, and where multi-week training
   experiments live, before QA.
5. The CI between integration and QA runs **locally**; GitHub Actions run only at the passage to
   production.

The cross-project convention (skill `environments`, its ADR-0001 and ADR-0002) satisfies needs 1,
3 and 5 as is: `main` + short branches, staging as an environment deployed from `main`, a signed
tag as the only trigger of GitHub Actions. It rejects a fixed `dev` tier because, for a solo
developer, an integration branch adds synchronisation cost for no value, and asks to revisit when
contributors with long-lived branches appear. Need 4 is exactly that revisit.

Two facts reframe the discussion:

- **Staging is an environment, not a branch.** What goes through QA is a commit deployed on the
  bench device; a `staging` branch would add a third long-lived branch to keep in sync (double
  merges, hotfixes to propagate) without giving anything the environment does not already give.
- **aristech is public** (cross-project ADR-0005): GitHub Actions minutes are free and unlimited
  here. The local CI is still the right choice, for determinism and independence from GitHub, not
  for cost.

## Options (MCDA)

Script: [`mcda/adr_0025_branching_model.py`](mcda/adr_0025_branching_model.py). Scores 0–5,
weights /100, totals /500; scores are estimates.

| Option | `main` field-ready 20 | Contributors, long experiments 20 | Local CI, Actions prod only 10 | Simplicity, no drift, hotfix 15 | QA before users 15 | Convention conformance 10 | Traceability of the field commit 10 | Total |
|---|---|---|---|---|---|---|---|---|
| A. git-flow `dev` → `staging` → `main` | 5 | 5 | 5 | 1 | 5 | 1 | 3 | 380 |
| B. `main` + short branches, staging environment, signed tag (the convention) | 4 | 3 | 5 | 5 | 5 | 5 | 5 | **440** |
| C. B + a `dev` integration branch | 5 | 5 | 5 | 3 | 5 | 2 | 4 | 430 |

Sensitivity: contributors 30 and simplicity 5 → **C 450**, A 420, B 420; `main` field-ready 30
and simplicity 20 → B 450, C 435. A is never first: the `staging` branch costs synchronisation and
brings nothing over the environment. **B vs C is fragile (10 points)** and hinges on one question:
do contributors arrive soon? The owner weighs contributors and training experiments higher than
the matrix's default and **chose C**. C is B plus one branch: the hooks, recipes, staging
environment and tag procedure are identical, so moving from B to C later would have cost nothing,
but the owner prefers to set the integration habit before the first contributor joins.

## Decision

Three long-lived refs and one environment:

| Ref / environment | Role | Enters by | Checks |
|---|---|---|---|
| `feat/*`, `fix/*`, `docs/*`, `research/*`, `refactor/*`, `chore/*`, `ci/*` | one issue each, from `dev` | push | `just check` (pre-push hook) |
| `dev` | integration: always green, what contributors clone and merge into | squash-merge PR | `just gate` attested on the head SHA, every review comment handled, owner approval |
| `staging` (environment, bench device; `just gate` locally until the device exists) | QA, the product without end users | `just deploy staging` from a `dev` commit | QA pass (skill `qa-browser-check`), `just attest staging` |
| `main` | field-ready: every commit is installable at the apiary | **merge-commit** PR `dev` → `main` of a QA-passed commit | the `gate` and `deploy/staging` attestations of that commit; owner approval |
| tag `vX.Y.Z` (signed) | production: device install and model publication, when they exist | the owner cuts it on `main` | the only trigger of GitHub Actions |

- `dev` → `main` is a **merge commit, never a squash**: the SHA that passed QA must be the one
  that reaches `main`, otherwise its attestations mean nothing.
- **Hotfix**: branch from `main`, PR to `main` with the same gate and QA, then `main` is merged
  back into `dev` at once (fast-forward or merge commit) so the fix is never lost.
- **Dependabot** targets `dev`; nothing reaches `main` without the integration step.
- **Rulesets** (public repository, free): no direct push and a pull request required on `main`
  and `dev`; merge commit only on `main`; `v*` tags owner-only and signed (skill `release-tag`).
  No required status check yet: the `gate` commit status arrives with brick 3 of agents-skills#210.
- There is **no `staging` branch**, and `dev` is a branch, not an environment tier: the tier
  names stay `local`, `staging`, `prod`.
- The promotion flow is drawn in
  [`architecture/diagrams/promotion/01-activity.md`](../architecture/diagrams/promotion/01-activity.md).

## Consequences

- Derogation to the cross-project convention (no fixed `dev`), to record in its derogations table
  with this ADR as the reason; re-evaluate if aristech stays single-developer for a year.
- `CONTRIBUTING.md` changes: branch from `dev`, PR to `dev`, the hotfix path, the merge-commit rule.
- #109 (local CI) wires `just check` on pre-push and `just gate` for every merge, whatever the
  target branch; `just deploy staging` waits for the bench device (ADR-0017) and gets its own issue.
- #110 removes or reduces the check workflows: `main` and `dev` are protected by the local gate,
  not by a GitHub job. CodeQL on a public repository is re-examined there.
- The open PRs that target `main` at the time of the switch are retargeted to `dev`.
- Two long-lived branches cost one extra merge per release and one back-merge per hotfix; the
  owner accepts that cost for the integration habit.
