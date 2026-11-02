# Conception gate — health-push (issue #158)

| Item | Status | Evidence |
|---|---|---|
| Spec complete, testable acceptance criteria | ✅ | `specs/health-push.md` (AC1–AC7) |
| UML updated | ✅ | `diagrams/health-push/01-state.md`, `02-sequence-heartbeat-fault.md`; UC11 in the product use-case diagram |
| ADR accepted | ✅ | ADR-0033 (owner chose daily heartbeat 395, loop error + live source ended 440, per-kind cool-down 450; 2026-11-02) |
| Dependency rule kept | ✅ | `health.py` in `application/`, stdlib only, reuses the `Clock` port; no new port (two `Notifier` methods) |
| Test strategy | ✅ | Unit with a hand-written fake clock and recording notifier: heartbeat period, rate limit, loop error, source end, Telegram push and delayed queue, CLI `health` section |
| Risks | ✅ | A hung camera is only seen through the missing heartbeat; up to 24 h to notice a dead unit; port change → every `Notifier` implements two more methods (two adapters) |

## Sign-off

- Owner: Benoît Bremaud — ☑ approved plan, options C, B, B (date: 2026-11-02)
