# ADR-0027: Local CI tiers with just, lefthook and mise

- Status: Accepted (owner, 2026-10-30)
- Date: 2026-10-30 (issue #109)
- Related: ADR-0025 (promotion model: local checks before `dev`, GitHub Actions on the signed tag
  only), ADR-0007 (security CI baseline), ADR-0026 (frozen environment records)

## Context

`ci.yml` is aristech's only automated check. The cross-project wave benoit-bremaud/agents-skills#259
moves the checks from GitHub Actions to the developer machine, and ADR-0025 places them between a
work branch and `dev`. aristech had no local tier: no `justfile`, no git hook, and a
`.pre-commit-config.yaml` that was never installed. Baseline measured on 2026-10-30: coverage 98 %,
gitleaks clean, Semgrep `p/python` 0 findings, zizmor 4 unpinned actions and 3 credential-persistence
findings, typos 45 false positives (French, author names), osv-scanner 4 vulnerable packages (fixed
by ADR-0026).

## Options (MCDA)

Script: [`mcda/adr_0027_local_ci_tiers.py`](mcda/adr_0027_local_ci_tiers.py). Scores 0–5, weights
/100, totals /500.

**D1 — hook runner and toolchain.**

| Option | Same checks everywhere 30 | Pinned, reproducible 25 | Speed 15 | Simplicity 15 | Cross-project fit 15 | Total |
|---|---|---|---|---|---|---|
| A. just + lefthook + mise | 5 | 5 | 4 | 4 | 5 | **470** |
| B. pre-commit framework (install the existing config) | 3 | 4 | 3 | 4 | 2 | 325 |
| C. Makefile targets + hand-written git hooks | 3 | 1 | 4 | 3 | 2 | 250 |

Sensitivity: simplicity 35 → A 450, B 335; reproducibility and parity 70 → A 480, B 330. A stays
first. B only covers the commit hook; the pre-push and pre-merge tiers would still need a runner.

**D2 — Semgrep when its rule registry is unreachable.**

| Option | No false green 50 | Works offline 30 | Simplicity 20 | Total |
|---|---|---|---|---|
| A. Print `WARNING … not run` and go on | 4 | 5 | 4 | **430** |
| B. Fail the check | 5 | 0 | 5 | 350 |
| C. Vendor the `p/python` rules in the repository | 5 | 5 | 1 | 420 |

Sensitivity: offline 50 → A 450; no-false-green 70 → C 440, B 425, A 415. A wins unless a skipped
SAST step is judged worse than a vendored rule set to maintain; the warning keeps the skip visible,
and the pre-merge review reports it as not green.

## Decision

- Toolchain pinned in `mise.toml`, checksums in `mise.lock`: just, lefthook, ruff (aqua), mypy
  (pipx, with `types-PyYAML`), typos, actionlint, zizmor, gitleaks, osv-scanner, Semgrep Community
  Edition (pipx). Python, the project venv and `sonar-scanner` stay outside mise.
- `justfile` tiers:
  - `fast` (L0, pre-commit hook): gitleaks on the staged changes, ruff on staged Python files,
    typos, actionlint on staged workflows.
  - `check` (L1, pre-push hook) = `lint` (ruff check and format, mypy, typos, actionlint, zizmor,
    `scripts/test-local-ci.sh`) + `test` (unit tests, coverage floor 80 %) + `security` (Semgrep
    `p/python` on `src` and `scripts`, osv-scanner on `requirements.txt`) + `secrets` (gitleaks on
    the full history).
  - `gate` (L2, before merge) = `check` + the SonarQube quality gate on the local server.
- `lefthook.yml` wires `fast` on pre-commit, the Conventional Commits subject check
  (`scripts/check-commit-msg.sh`) on commit-msg and `check` on pre-push.
- `.pre-commit-config.yaml` and the `pre-commit` dev dependency are removed.
- osv-scanner scans `requirements.txt` only; the frozen environment records under `docs/research/`
  are never installed (ADR-0026) and stay out of the scan.
- `_typos.toml` accepts the French words, author names and package names of the documents.
- Workflows: every action pinned by commit SHA, `persist-credentials: false` on every checkout.

## Consequences

- Measured on 2026-10-30: `just check` about 20 s, `just fast` under 1 s.
- lefthook installs its hooks in the shared git directory, so every worktree gets them; on a
  checkout without `lefthook.yml` (an older branch) the hooks print a notice and pass.
- "Unreachable" means the `p/python` rule URL does not answer; any other Semgrep error fails the
  check. Semgrep runs with `EIO_BACKEND=posix`: its default io_uring backend failed intermittently
  under the machine's locked-memory limit.
- `ci.yml` still runs on pull requests until #110 reduces or removes it.
- The QA pass and the attestation of the gate (`gate` commit status, staging note) come with the
  cross-project tooling (ADR-0025).
