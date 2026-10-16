# Local review — aristech (branch diff main...docs/b1-adrs)

- Date: 2026-10-16
- Commit: e148a8d (fixes below landed in the next commit)
- Scope: branch diff `main...HEAD` — `docs/decisions/ADR-0001..0008`, `docs/decisions/README.md`,
  `CLAUDE.md`
- Checks run: docs · correctness (claims checked against `PROJECT_LOG.md`, `requirements.md`,
  the audit and the code; MCDA arithmetic recomputed) (design · tests · security not applicable)
- Verdict: ship after fixes · Must 0 · Should 3 (2 fixed, 1 deferred) · Nice 3 (fixed)

## 🔴 Must Have

_None._ (Before the review, a scripted recomputation corrected 12 mis-added MCDA totals; no
ranking changed.)

## 🟡 Should Have

- `docs/decisions/ADR-0004-operating-point-zero-bee-threshold.md:30` `[docs]` · script attributed
  to #18 (issue) · fixed: PR #37, issue #18.
- `docs/decisions/ADR-0004-operating-point-zero-bee-threshold.md:26` `[docs]` · contradicts the
  "high confidence threshold" wording of `requirements.md:108` · fixed: ADR states it refines that
  wording (requirements refresh belongs to the docs-freshness brick).
- `docs/decisions/ADR-0007…:4`, `ADR-0008…:4` `[docs]` · PRs #49 and #51 not yet in
  `PROJECT_LOG.md` · deferred: covered by the B1 log PR after merge.

## 🔵 Nice to Have

- `ADR-0002:14` `[docs]` · VespAI is YOLOv5s + ResNet · fixed: states which part is wrapped.
- `ADR-0007:19` `[correctness]` · option A cost scored as high as Gitleaks-only · fixed: 5 → 4
  (total 440, still first).
- `ADR-0003` `[docs]` · shared legal basis with ADR-0005 not linked · fixed.

## ⚪ Disagree / Intentional

- All ADRs `[docs]` · repeated 3-line "retroactive" notice · intentional: each ADR must stand
  alone.

## Per-dimension summary

- Docs: 8/8 decisions recorded, claims verified · Correctness: MCDA consistent, option A highest
  everywhere.
