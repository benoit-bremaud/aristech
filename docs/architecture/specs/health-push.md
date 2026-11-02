# Spec — health push: tell the beekeeper the unit is alive, or broken

> **Status**: Accepted — built (issue #158) · **Related**: ADR-0006, ADR-0032, ADR-0033, UC11 ·
> **UML**: [state](../diagrams/health-push/01-state.md),
> [sequence](../diagrams/health-push/02-sequence-heartbeat-fault.md)

## Need

A unit at a remote apiary that stops working says nothing. The beekeeper must learn that the unit
works, and be told when it detects a fault it can still report, without a flood of messages.

## Actors

- **Beekeeper** (primary) — checks that the unit is alive and acts on a fault (UC11).

## Main scenario

1. The unit runs the detection loop with the push channel enabled (`--push telegram`).
2. Once per heartbeat period (24 h by default), it pushes an alive message: uptime, frames
   processed, attack episodes.
3. The beekeeper sees the daily message and knows the unit works.

## Alternative scenarios

- **A1** The detection loop raises an error → a `loop_error` fault is pushed, then the run stops
  with the error (open episode summarised, source closed).
- **A2** The live camera source stops sending frames → a `source_ended` fault is pushed. The end of
  a video file is not a fault.
- **A3** The same fault kind repeats within the cool-down (1 h) → it is logged, not pushed, and
  counted in the next push of that kind.
- **A4** The unit dies, hangs or loses the network → no heartbeat arrives; the beekeeper notices
  the missing message (server-side watchdog with M6).
- **A5** The push channel is down → the message waits in the delayed queue (ADR-0032 A1).

## Acceptance criteria

- **AC1** A heartbeat is sent when the period has elapsed on the wall clock, never before, and the
  next one waits a full period.
- **AC2** A loop error is sent as a fault before the error is raised again.
- **AC3** The end of a live source is a fault; the end of a video file is not.
- **AC4** At most one push per fault kind per cool-down; muted faults are counted.
- **AC5** Period and cool-down are configuration values (`health` section).
- **AC6** The pushed fault holds no exception text; secrets never appear (ADR-0032 AC8).
- **AC7** The rule is pure and unit-tested with a fake clock and a fake notifier.

## Verification (issue #158)

Unit tests: `test_health.py` (AC1, AC4, AC7), `test_detect_hornet_visual.py` (AC2, AC3),
`test_telegram_notifier.py` and `test_logging_notifier.py` (AC6, A5), `test_cli_wiring.py` (AC3,
AC5).
