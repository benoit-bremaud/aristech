# Conception gate — operating point (M4, issue #18)

| Item | Status | Evidence |
|---|---|---|
| Spec complete, testable acceptance criteria | ✅ | `specs/operating-point.md` (AC1–AC6) |
| UML updated | ✅ | `diagrams/operating-point/01-activity.md`; the class diagram covers the live path only, the evaluation types are not modelled there |
| ADRs accepted | ✅ | ADR-0029 (owner chose C, 360/500, first in 70 % of weight vectors), on top of ADR-0014 |
| Dependency rule kept | ✅ | Only `evaluation/` (pure) and `scripts/` change; RF-DETR stays a lazy import |
| Test strategy | ✅ | Unit: margin, false-alert cap, bound, no safe threshold, negative margin (AC2–AC4); script argument checks; AC5 already covered by the `decide` tests; AC6 is the local measurement in `docs/research/operating-point-test-v1.md` (needs the checkpoint, not in CI) |
| Risks | ✅ | test-v1 is internet data, not the field: the threshold is provisional (ADR-0029) |

## Sign-off

- Owner: Benoît Bremaud — ☑ approved (date: 2026-11-02, option C: zero bees with margin + false alerts ≤ 2.5 %, provisional threshold)
