# Spec — YAGNI ports and legacy training removal (brick B5)

> **Brick**: B5 · **Audit**: S1, S3, S6 · **Decision**: ADR-0010 · **Out of scope**: S2 refresh of
> `docs/architecture.md` beyond dead references (B6)

## Need

The code base carries only what a present use case, test or adapter needs. A reader no longer meets
ports, domain types, extras or a Keras pipeline that nothing uses, and the dataset split helper that
M5 (YOLO fine-tune) needs survives the legacy package.

## Acceptance criteria

- **AC1** `application/ports/` holds only `VideoSource`, `HornetDetector`, `Notifier`; `Actuator`,
  `AudioSource`, `Clock`, `DistanceSensor`, `SoundClassifier` are deleted (S1).
- **AC2** `Target`, `Point3D`, `AudioSample` and their tests are deleted; `Point2D` stays
  (`BoundingBox.center`) (S1).
- **AC3** `src/aristech/training/`, `tests/model_training/`, `scripts/train_model.py` are deleted
  (S3, S6).
- **AC4** `distribute_files` moves unchanged to `aristech.datasets.distribute`; its unit tests move
  to `tests/unit/datasets/`; `scripts/distribute_images.py` and `distribute_videos.py` import it
  from there.
- **AC5** `pyproject.toml` has no `training`, `audio` or `connectivity` extra, no mypy override
  for `aristech.training.*`, no ignore for `tensorflow.*`/`pyaudio`; `requirements.txt` is relocked
  if it lists them.
- **AC6** `grep -rE "aristech\.training|tensorflow"` over `src tests scripts pyproject.toml Makefile
  .github` returns nothing.
- **AC7** `make test-unit`, `make type-check`, `make lint`, `ruff format --check` are green.

## Design impact

Structure changes (ports, extras) → ADR-0010 supersedes the extras list of ADR-0001. UML: the
component and class diagrams already omit the speculative types; their notes are updated and the
component diagram gains the `datasets` helper.
