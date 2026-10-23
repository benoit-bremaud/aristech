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
  sample of 1,453 frames (ADR-0021 step 1). Owner approved 2026-10-22.
- PR 3: Sledevic frames are renamed `<hive session>_<frame>` so the existing `video` group rule keeps
  one landing board per group (8 groups; no board in two splits). The files came from Mendeley's
  public API with each file's SHA-256 checked; no login was needed after all.
- PR 3: the owner delegated the box correction (ADR-0018) to the agent. Boxes come from Grounding
  DINO tiny zero-shot; the agent reviewed every overlay and kept only images with one correct
  box (282 of 450). Details and the exclusion reasons: `qa/2026-10-22-annotation-pipeline-pr3.md`.
- PR 3: `split_by_group` fix. Once a frozen set exists, the other groups go to train or
  validation only; before, each re-split sent 15 % of them to `test`, so the test split grew
  beyond the frozen set (288 → 556). Spec AC5 unchanged; a future `test-v2` needs its own option.
- PR 4 (2026-10-23): size, scoring path and the human box check were not designed. Added
  ADR-0024 (RF-DETR Small, `RFDETRDetector` + UC3 harness, 30-image contact sheet), spec AC11 and
  main step 6, sequence `05-sequence-train-score.md`. Owner approved 2026-10-23.

## Sign-off

- Owner: Benoît Bremaud — ☑ approved (date: 2026-10-19)
