# Conception gate — annotation pipeline + first pre-field model (issue #95)

| Item | Status | Evidence |
|---|---|---|
| Spec complete, testable acceptance criteria | ✅ | `specs/annotation-pipeline.md` (AC1–AC9, A1–A7) |
| UML updated | ✅ | `diagrams/annotation-pipeline/` (use-case, sequence, class, data-flow) |
| ADRs with scripted MCDA | ✅ | ADR-0018 to ADR-0022, `decisions/mcda/adr_0018_0022_annotation_pipeline.py` |
| Dependency rule kept | ✅ | Stdlib-only `datasets/` module (no port, ADR-0010); training in `scripts/` + optional extra `train` |
| Licences recorded | ✅ by design | Licence register + allow-list enforced at import (AC1) |
| Test strategy | ✅ | Unit (stdlib, CI): register allow-list, class map, group keys (Roboflow stem, C1 sidecar), deterministic group split, frozen-set violations. Real import/training/report run locally, recorded in the report (data and weights not in CI). |
| Risks | ✅ | Roboflow/Mendeley pages need login → owner downloads. Fragile MCDAs (0018, 0021, 0022) are reversible: format/manifest are the contract. Hailo support for RF-DETR unverified → decided at M6. |

## Delivery staircase

1. PR 1 — this dossier.
2. PR 2 — `.gitignore` whitelist for `data/registry/`, `datasets/` registry, import, group split, freeze + CLI script; Roboflow + Sledevic imported.
3. PR 3 — iNaturalist increment, annotation, `test-v1` frozen.
4. PR 4 — RF-DETR training script (`train` extra) + first-model report vs VespAI on `test-v1`.

## Deviations during delivery

- PR 2 (2026-10-22): the Sledevic bee set moves to PR 3. Its Mendeley download needs the owner's
  login; the register gets its row only once the files are retrieved (a row without data would
  record an unverified licence). The design is unchanged.
- PR 2: class and sequence diagrams redrawn as built (register as functions plus `LicenceError`,
  `group_rule`, `FrozenRow`, label snapshot, every frozen set auto-discovered by `split`).

- PR 3 (2026-10-22): how iNaturalist photos are fetched was not designed. Added ADR-0023
  (stdlib `scripts/inat_fetch.py`, per-photo attribution file, group rule `observation`),
  spec AC10 and A8, and the fetch step in the sequence diagram. Sledevic is imported as a capped
  sample of 1,500 frames (ADR-0021 step 1). Owner approved 2026-10-22.

## Sign-off

- Owner: Benoît Bremaud — ☑ approved (date: 2026-10-19)
