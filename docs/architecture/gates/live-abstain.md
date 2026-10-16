# Conception gate — live-abstain (brick B4)

| Item | Status | Evidence |
|---|---|---|
| Spec complete, testable acceptance criteria | ✅ | `specs/live-abstain.md` (AC1–AC6) |
| UML updated | ✅ | `diagrams/detection/02-sequence-live-detection.md`, `04-class.md` (`notify_abstention`) |
| ADRs accepted | ✅ | ADR-0009 (owner validated options 1A 440/500, 2A 470/500) |
| Dependency rule kept | ✅ | Only `application/` port + use case and `interface/cli` change; no new import direction |
| Test strategy | ✅ | Unit: use case with hand-written fakes (AC1–AC3, AC6), `LoggingNotifier.notify_abstention`, CLI wiring via fake adapters (AC4, AC5). No integration change (VespAI weights not in CI). |
| Risks | ✅ | Floor too low → more boxes per frame (CPU); mitigated by default 0.1. Port change → every `Notifier` must implement the new method (one adapter today). |
| ABSTAIN logged? | ✅ | Yes, INFO on `aristech.detection`, distinct `abstain` wording. |

## Sign-off

- Owner: Benoît Bremaud — ☑ approved (date: 2026-10-16)
