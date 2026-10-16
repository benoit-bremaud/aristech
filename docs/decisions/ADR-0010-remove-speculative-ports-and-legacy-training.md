# ADR-0010: Remove speculative ports, unused extras and the legacy Keras training package

- Status: Accepted
- Date: 2026-10-16 (brick B5, owner-validated weights and options)
- Supersedes: the list of extras in ADR-0001 (`audio`, `training`, `connectivity`)

## Context

The audit (S1, S3, S6) found five ports with no consumer and no implementation, three domain types
used only by them, a Keras `training/` package that no port uses (M5 is a YOLO fine-tune, not
Keras), its false-confidence tests, and extras with no adapter. One module of `training/`,
`distribute.py`, is a generic, tensorflow-free train/val/test file splitter used by the dataset
scripts. Spec: `docs/architecture/specs/yagni-training-removal.md`.

## Decision 1 — fate of `distribute_files`

Criteria and weights: YAGNI 30, usefulness for M5 30, simplicity 20, architecture coherence 20.

| Option | C1 | C2 | C3 | C4 | Total /500 |
|---|---|---|---|---|---|
| A. Move to `aristech.datasets.distribute` with its tests | 3 | 4 | 4 | 4 | **370** |
| B. Delete it with the scripts | 5 | 1 | 5 | 4 | 360 |
| C. Keep `training/` reduced to `distribute` | 3 | 4 | 4 | 1 | 310 |

Sensitivity: B overtakes A if usefulness for M5 weighs under ~25. **Chosen: A.**

## Decision 2 — extras without an adapter (`audio`, `connectivity`)

Criteria and weights: YAGNI 40, "a seam needs a present force" rule 30, reintroduction cost 30.

| Option | C1 | C2 | C3 | Total /500 |
|---|---|---|---|---|
| A. Delete them | 5 | 5 | 4 | **470** |
| B. Keep them | 1 | 2 | 5 | 250 |

Robust to any reasonable weight change. **Chosen: A.**

## Consequences

- Extras are now `vision` and the tooling extras only; `audio`/`connectivity` come back with their
  first adapter, together with the port it implements.
- The speculative ports and `training/` remain readable in git history.
- `tensorflow` leaves the project; the `importorskip("tensorflow")` guards go with their tests.
