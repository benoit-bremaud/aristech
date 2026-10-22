# Pre-push review — `feat/dataset-registry-import-split`

> **Scope**: PR 2 of issue #95, after the signed gate `annotation-pipeline`: stdlib module
> `aristech.datasets` (`registry.py`, `manifest.py`, `split.py`), CLI `scripts/dataset.py`
> (`import`, `split`, `freeze`), committed `data/registry/` (licence register + 364-row Roboflow
> manifest), `.gitignore` whitelist, INSTALL section, as-built class / sequence / data-flow
> diagrams, gate deviations, traceability UC8.

## Checks

- `ruff check`, `ruff format --check` (src, tests), strict `mypy`: clean.
- Unit tests: 222 passed, 2 skipped (OpenCV absent locally); coverage of the new modules: 100 %
  `manifest.py`, 100 % `registry.py`, 98 % `split.py`.
- Dependency rule: `datasets/` imports the stdlib and `domain.capture` only; no new port (ADR-0010),
  no new dependency.
- Licences: the only registered source is CC-BY-4.0 with its attribution; no pixels committed
  (`data/registry/` holds CSV only).
- QA on the real export: [qa/2026-10-22-dataset-registry.md](../qa/2026-10-22-dataset-registry.md).
- Secrets scan: gitleaks on the branch commits and the touched folders, no leaks.

## 🔴 Must Have (all fixed)

- `split` without `--frozen` could reassign a frozen test set → `split` now discovers and enforces
  every `test-v*.csv`; frozen groups are found by image membership, not by name.
- The group join kept a single target, so a third group sharing an image escaped it → union-find,
  first-seen group name wins.

## 🟡 Should Have (all fixed)

- A duplicate image inside one import produced one row → one row per copy, so their groups join.
- `freeze` could leave a half-written snapshot or copy a stale store label → staged snapshot then
  rename; every store label hash checked first.
- `load_frozen` trusted the snapshot → it verifies the columns, the digest file and each label hash.
- Errors did not name the label file; an empty `--class-map` passed; `captive` was mandatory →
  fixed.
- Violation tests asserted "some violation" → exact counts, tamper cases parametrized, captive
  control case.

## 🔵 Nice to Have (deferred)

- A crash between snapshot copy and rename leaves `.test-vN-labels.tmp`; the next `freeze` removes it.
- No `verify` subcommand: `split` already verifies every frozen set.

## Disagree

- None.

## Not verifiable here

- Sledevic import (owner login on Mendeley) → PR 3, recorded in the gate deviations.
- AC7–AC8 (first model, report) → PR 4.

## External review round (PR #99)

- Fixed: `split` and `freeze` did not re-check licences → every manifest source must still pass
  `require` (a revoked or NC licence exits 2).
- Fixed: `freeze --id foo` wrote a set `split` never discovers → ids must match `test-v<N>`
  (also blocks path separators).
- Fixed: duplicate images with different labels left the store out of step with the manifest →
  the import refuses them.
