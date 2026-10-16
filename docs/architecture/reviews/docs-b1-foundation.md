# Local review — aristech (branch diff main...docs/b1-foundation)

- Date: 2026-10-16
- Commit: 2fd9937 (fixes below landed in the next commit)
- Scope: branch diff `main...HEAD` — `CLAUDE.md`, `docs/architecture/**`, `docs/decisions/README.md`,
  `docs/INDEX.md`
- Checks run: docs · correctness (design · tests · security not applicable: documentation only)
- Verdict: ship after fixes · Must 2 (fixed) · Should 4 (3 fixed) · Nice 2 (fixed)

## 🔴 Must Have

- `docs/INDEX.md:31,69` `[docs]` · INDEX still named `architecture.md` the design authority and
  sent decisions there, ignoring the new dossier and ADRs · fixed: dossier + ADR rows added,
  `architecture.md` marked legacy, decisions routed to `docs/decisions/`.
- `CLAUDE.md:9,32` `[docs|correctness]` · layer list omitted `evaluation/` and `training/`; the
  heavy-import rule did not cover them · fixed: both named, `training/` recorded as the known
  exception (audit S3).

## 🟡 Should Have

- `CLAUDE.md:32` `[correctness]` · "`domain/` imports stdlib only" is false (`domain/target.py:5`)
  · fixed: "stdlib and `domain/` only".
- `docs/architecture/reviews/README.md:9` `[docs]` · prior report sat outside `reviews/` · fixed:
  moved to `reviews/ci-security-baseline.md`.
- `CLAUDE.md:24` `[docs]` · git workflow duplicated `docs/CONTRIBUTING.md` · fixed: link instead.

## 🔵 Nice to Have

- `CLAUDE.md` `[docs]` · MCDA line repeated a global rule · fixed: removed.
- `docs/architecture/README.md:4` `[docs]` · undefined "brick B6" reference · fixed: points to
  audit finding S2.

## ⚪ Disagree / Intentional

- `CLAUDE.md:44` `[docs]` · `uv pip install ... --no-deps` for the tools may skip pytest deps ·
  this is the dev-env command validated on 2026-10-16 (B2); `make install-dev` pulls the full
  heavy lock, which is what the command avoids.

## Per-dimension summary

- Design: n/a · Docs: all links resolve, facts match Makefile/pyproject · Tests: n/a ·
  Security: n/a · Correctness: one false import claim, fixed.
