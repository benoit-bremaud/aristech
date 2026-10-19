# Conception gate — capture-rig (brick C1)

| Item | Status | Evidence |
|---|---|---|
| Spec complete, testable acceptance criteria | ✅ | `specs/capture-rig.md` (actors, main + A1–A6 scenarios, AC1–AC9 with verification) |
| UML updated | ✅ | `diagrams/capture-rig/` 01 use-case, 02 sequence, 03 component, 04 state |
| ADRs accepted | ✅ | ADR-0017 (owner validated 2026-10-19: board A 400, camera A 400, mics A 425, storage C 410; BOM ≈ 345 €, prices to confirm at order) |
| Dependency rule kept | ✅ | Hardware libraries in `infrastructure/capture/` behind the `capture` extra; application uses ports only |
| Test strategy | ✅ | Unit: `RecordCampaign` with fake camera, audio, store and clock (AC3, AC4, AC7, AC8). Field: clap test (AC1), 7-day run (AC2), ruler test (AC6), power log (AC9). No hardware in CI. |
| Risks | ✅ | I²S cable run to the colony mic (fallback: line driver); Pi 5 software encode load (measured at AC9); heat in the head in summer (vents, roof); delivery lead time vs July 2027 |

## Sign-off

- Owner: Benoît Bremaud — ☑ approved (date: 2026-10-19)
