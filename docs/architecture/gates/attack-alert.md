# Conception gate — attack-alert (issue #149)

| Item | Status | Evidence |
|---|---|---|
| Spec complete, testable acceptance criteria | ✅ | `specs/attack-alert.md` (AC1–AC7, provisional `N`/`W`/`T`) |
| UML updated | ✅ | `diagrams/attack-alert/01-state.md`, `02-sequence-live-alert.md`; operating-point activity note |
| ADRs accepted | ✅ | ADR-0031 (owner chose COUNT B 410/500 and episode rule E1 415/500, 2026-11-02) |
| Dependency rule kept | ✅ | `attack_episode.py` in `application/`, stdlib only; no new port (two methods on `Notifier`) |
| Test strategy | ✅ | Unit: tracker with scripted timestamps (AC1, AC4), use case with hand-written fakes (AC2), `select_count_point` and `image_point`, CLI wiring (AC3, AC6), video time on a generated clip (AC7). Sample-video run with RF-DETR (local, weights not in CI). |
| Risks | ✅ | COUNT sits on the precision target (fragile); values provisional until M5. Port change → every `Notifier` implements two methods (one adapter today). |

## Sign-off

- Owner: Benoît Bremaud — ☑ approved plan, options B and E1 (date: 2026-11-02)
