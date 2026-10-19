# Conception gate — M3 report (VespAI baseline)

| Item | Status | Evidence |
|---|---|---|
| Spec complete, testable acceptance criteria | ✅ | `specs/m3-report.md` (AC1–AC6) |
| UML updated | ✅ n/a | Offline evaluation flow unchanged (runner → metrics); no new diagram |
| ADRs accepted | ✅ n/a | No structuring choice: one script + Makefile target over the existing harness |
| Dependency rule kept | ✅ | New code only in `scripts/` and `Makefile`; VespAI imported lazily as in M4 |
| Test strategy | ✅ | Unit: argument parsing, path checks (A1–A3), single detector pass and per-threshold table with a hand-written fake detector. Real VespAI run is local (weights not in CI), recorded in the report. |
| Risks | ✅ | Dataset re-download may differ from the 2026-05 copy → report pins version and split sizes; mismatch is reported, not hidden. Weights are a pickle → loaded only from a trusted path (INSTALL.md). |

## Sign-off

- Owner: Benoît Bremaud — ☑ approved (date: 2026-10-19)
