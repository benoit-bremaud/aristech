# Local review — aristech (branch `docs/112-branching-model`)

- Date: 2026-10-30
- Commit: 0dd71c5 (findings applied in the follow-up commit of the same branch)
- Scope: branch diff `origin/main...HEAD` — ADR-0025, promotion activity diagram, conception gate,
  `CONTRIBUTING.md`, `docs/decisions/README.md`, Dependabot target branch, MCDA script
- Checks run: docs · correctness · security (secrets + diff read) · execution checks. Design and
  test-quality agents not run: no `src/` or `tests/` change
- Verdict: fix Should Have first, then push · Must 0 · Should 8 · Nice 5

## Pre-push gate (head SHA 0dd71c5)

| Step | Result |
|---|---|
| 1 Tests | ✅ 270 unit passed, 5 deselected (hardware / model markers) |
| 2 Coverage | tests 98 % lines (floor 80) · docs: not measured, no counter in the project; docs-only diff |
| 3 SonarQube | ⚠️ not run: Community Build analyses `main` only (`CLAUDE.md`) |
| 4 Secrets | ✅ gitleaks clean (`origin/main..HEAD`) · tracked `.env.example` is the placeholder template · diff read: nothing sensitive |
| 5 QA pass | skipped: `--push` mode, docs-only diff |
- Gate: **push authorised once the Should Have below are applied** (merge gate re-run on the PR head)

## 🔴 Must Have

_None._

## 🟡 Should Have

- `docs/architecture/diagrams/promotion/01-activity.md:29,33,41,46` `[correctness]` · cross-partition edges declared inside another subgraph can draw H, I, N, P in the wrong lane · declare nodes in their own subgraph, edges after all subgraphs — applied
- `.github/dependabot.yml:6` + ADR § Decision `[docs][correctness]` · Dependabot reads its config on the default branch and its security updates ignore `target-branch` · owner decision: `dev` becomes the default branch (A 445 vs B 300) — recorded in ADR and CONTRIBUTING
- ADR § Consequences `[docs]` · `dev` must exist on origin before the PR merges or the weekly Dependabot run fails · bootstrap bullet added
- ADR § Decision hotfix bullet `[docs]` · "fast-forward or merge commit" back-merge impossible under a required-PR ruleset on `dev` · "merge-commit pull request" — applied
- `docs/CONTRIBUTING.md:57` `[docs]` · work-cycle step 1 names no base branch · "from `dev` (from `main` for a hotfix)" — applied
- `docs/CONTRIBUTING.md:127` `[docs]` · "No force-push to `main`" omits `dev` — applied
- `docs/architecture/gates/promotion.md:3-5` `[docs]` · "five rules" (six bullets); no spec, the ADR stands in and should say so — applied
- ADR § Consequences `[docs]` · statements that #109/#110 will make stale (CONTRIBUTING step 5 "CI 3.10–3.12", `pre-commit install`, PR template "private R&D", "CI green") were not tracked · listed under the #109 and #110 bullets — applied

## 🔵 Nice to Have

- `docs/decisions/mcda/adr_0025_branching_model.py:29,33` `[docs]` · docstrings and best-first sort as in `adr_0024` — applied
- ADR § Options `[docs]` · name the owner's sensitivity scenario — applied ("owner weights")
- `01-activity.md` `[docs]` · "swimlanes" → partitions; hotfix lane linked to the tag and to the back-merge — applied
- `docs/decisions/mcda/adr_0018_0022_annotation_pipeline.py:73` `[correctness]` · pre-existing `B905` (`zip` without `strict`), outside this diff · follow-up, not touched
- `.github/PULL_REQUEST_TEMPLATE.md:1` `[docs]` · "private R&D project", "CI green" stale against ADR-0005 and the local gate · tracked for #110

## ⚪ Disagree / Intentional

- `docs/CONTRIBUTING.md:15` (`pre-commit install`) and `:77` (CI 3.10–3.12) `[docs]` · still true today: `ci.yml` runs on every pull request whatever the base; retired by #109 and #110, recorded in the ADR consequences

## Per-dimension summary

- Design: n/a (no code) · Docs: four documents consistent on branch names, squash vs merge commit, hotfix, Dependabot; default-branch gap closed · Tests: n/a · Security: clean · Correctness: Mermaid partition edges fixed, MCDA totals match the script
