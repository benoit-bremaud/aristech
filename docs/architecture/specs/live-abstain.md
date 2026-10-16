# Spec — live path: uncertain targets are visible as ABSTAIN

> **Brick**: B4 · **Audit**: M3 · **Related**: ADR-0003, ADR-0004, ADR-0006, ADR-0009, issue #18

## Need

The operator must see, in the live path (UC1), every *V. velutina* detection the system chose not
to act on because it was not confident enough. Today the detector drops every box below the
operating threshold before the decision policy runs, so the ABSTAIN outcome is unreachable and
uncertain targets vanish silently. Without that signal the operating point (issue #18) cannot be
validated in the field.

## Actors

- **Operator** — runs the live detection and reads its log.

## Main scenario

1. The operator starts the live detection with an operating threshold `c` and a detector floor `f`
   (`f <= c`).
2. The detector reports every box at or above `f`.
3. For each detection the decision policy returns ACT, ABSTAIN or IGNORE against `c`.
4. ACT and ABSTAIN are both reported to the operator, distinguishably.

## Alternative scenarios

- **A1** `f > c` → the run is refused with exit code 2 and an error message.
- **A2** `f` or `c` outside `[0, 1]` → refused with exit code 2.
- **A3** `f` omitted → a default floor of 0.1 applies (clamped to `c` when `c < 0.1`).

## Acceptance criteria

- **AC1** A *V. velutina* detection with `f <= confidence < c` is reported as an abstention.
- **AC2** A *V. velutina* detection with `confidence >= c` is reported as a threat (ACT).
- **AC3** A detection of any other species (bee, other) never produces ACT nor an abstention report.
- **AC4** The detector is configured with `f`, the decision policy with `c`; the two are distinct.
- **AC5** `f > c` and out-of-range values are rejected with exit code 2.
- **AC6** The final summary counts threats and abstentions separately.
