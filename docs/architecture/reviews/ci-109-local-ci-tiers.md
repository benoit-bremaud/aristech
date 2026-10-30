# Pre-push review — ci/109-local-ci-tiers

Review of the local CI tiers (ADR-0027, issue #109) before the push.

- Date: 2026-10-30
- Scope: branch diff `origin/dev...HEAD`
- Checks run: design · docs · tests · security · correctness (adversarial pass on the diff)
- Verdict: ship · Must 0 (2 fixed) · Should 2 fixed · Nice 4 (2 fixed)

## Pre-merge gate

| Step | Result |
|---|---|
| 1 Tests | ✅ 270 unit passed · `scripts/test-local-ci.sh` OK (recipes, `lefthook validate`, commit-msg, staged secret refused) |
| 2 Coverage | tests 97.7 % (floor 80, enforced by `just test`) |
| 3 SonarQube | ✅ PASSED (`just gate`) |
| 4 Secrets | ✅ gitleaks full history clean · only `.env.example` tracked · diff read: the test AWS key is split and AWS's documented example |
| 5 QA pass | ✅ smoke: tooling-only diff; hooks exercised on the real commit (pre-commit, commit-msg) |

Measured: `just fast` under 1 s, `just check` about 15–20 s, `just gate` 26 s. Semgrep: a planted
`shell=True` finding fails `just security`.

## 🔴 Must Have

- `scripts/test-local-ci.sh:30` `[tests]` · any non-zero gitleaks exit (127 when missing) passed
  the staged-secret test · now requires exit 1 — fixed.
- `scripts/test-local-ci.sh:28` `[correctness]` · found by the first real push: inside a git hook
  `GIT_DIR` points at this repository, so the throwaway `git init` re-initialised it and set
  `core.bare=true` in the shared config (restored to `false`, index checked clean) · the script
  now unsets the `GIT_*` variables first; verified with `GIT_DIR` set, then by the pre-push hook
  (`just check` 36 s) — fixed.

## 🟡 Should Have

- `justfile` `gate` `[correctness]` · the `base` parameter had no effect · removed — fixed.
- `justfile` `security` `[correctness]` · a comment inside the recipe was echoed · moved above —
  fixed.

## 🔵 Nice to Have

- `docs/INSTALL.md` `[docs]` · mise needs `uv` for the pipx tools · documented — fixed.
- `.github/workflows/ci.yml` `[docs]` · CI runs a subset of `just check` (no typos, zizmor,
  Semgrep, osv, coverage floor) · #110 reduces or removes `ci.yml`.
- `lefthook.yml` `[correctness]` · no `skip: [merge, rebase]` · hooks are fast; revisit if a
  rebase gets slow.
- `_typos.toml` `[docs]` · short words (`sur`, `mis`, `nd`, `iy`, `Ba`, `UE`) ignored globally ·
  accepted: per-file rules would cost more than the typos they could catch.

## ⚪ Disagree / Intentional

- `justfile` `security` `[security]` · offline Semgrep exits 0 with a warning · owner decision
  ADR-0027 D2 A: the warning keeps the skip visible and the pre-merge review reports it as not
  green.
- `justfile` `gate` `[correctness]` · SonarQube scanned from a branch lands in the single project ·
  existing practice (`make sonar`, CLAUDE.md): Community Build has one branch; the gate judges the
  head that is about to merge.
