# Pre-push review — feat/dataset-registry-import-split (issue #95, PR 2)

Scope: `aristech.datasets` registry, manifest, split, freeze; `scripts/dataset.py`; committed
`data/registry/` (licence register + 364-row Roboflow manifest); INSTALL section; traceability UC8.

| Check | Result |
|---|---|
| Code review (correctness, dependency rule, KISS) | 2 Must, 4 Should — all fixed |
| Test audit | weak violation tests rewritten (exact counts, tamper parametrize, stale store, captive control) |
| Unit tests (`make test-unit`) | 222 passed, 2 skipped; datasets coverage 98–100 % |
| ruff check, ruff format --check, mypy | clean |
| Secrets scan (gitleaks, branch commits) | no leaks |
| QA on the real export | `docs/architecture/qa/2026-10-22-dataset-registry.md` — all steps as expected |
| Dependency rule | `datasets/` imports stdlib + `domain.capture` only; no new port, no new dependency |

## Must — fixed

1. `split` without `--frozen` could reassign a frozen test set: every `test-v*.csv` is now
   auto-discovered and enforced; frozen groups are found by image membership, not name.
2. Group join kept a single target: replaced by union-find, first-seen group name wins.

## Should — fixed

1. Duplicate image inside one import now yields one row per copy, so their groups join.
2. `freeze` is atomic (staged snapshot, then rename) and refuses a missing or stale store label.
3. `load_frozen` verifies each label-snapshot hash, the digest file and the columns.
4. Errors name the label file; an empty `--class-map` is refused; `captive` is optional.

## Nice — kept for later

Sledevic row added only once downloaded (needs owner login); `freeze` leaves a stale `.tmp` on a
crash between copy and rename (re-run cleans it); no CLI `verify` subcommand (split already checks).
