# Spec — M3 report: reproducible VespAI baseline on the Roboflow set

> **Brick**: M3 report · **Roadmap gate**: per-class P/R recomputable on demand ·
> **Related**: ADR-0002 (VespAI licence), ADR-0015 (own model, VespAI kept as baseline),
> `scripts/measure_operating_point.py` (M4)

## Need

ADR-0015 rests on one measured fact: VespAI's published F1 ≈ 0.99 does not transfer to an
independent set (recall ≈ 3–13 % on a public Roboflow *V. velutina* / *V. crabro* set). That
measurement was taken with throwaway scripts and is not a repository artefact, so it cannot be
checked or rerun. The owner needs the baseline that M5 must beat to be **recomputable on demand
by one command** and **recorded in a committed report** with everything needed to rerun it.

## Actors

- **Researcher** (the owner, or anyone rerunning the baseline) — supplies the weights, the
  YOLOv5 code and the dataset, runs the command, reads the report.

## Main scenario

1. The researcher installs the `vision` environment (`docs/INSTALL.md`) and obtains the VespAI
   weights, the pinned YOLOv5 commit and the Roboflow export, each from its documented source.
2. The researcher runs `make m3-report WEIGHTS=… YOLOV5_DIR=… DATASET=…`.
3. The command runs VespAI once (floor = lowest threshold) over the chosen splits and prints,
   for each reported confidence threshold, a per-class table: TP, FP, FN, precision, recall, F1 (Markdown).
4. The researcher compares the output with `docs/research/m3-vespai-baseline.md`; the numbers
   match.

## Alternative scenarios

- **A1** weights, YOLOv5 directory or dataset path missing → exit code 2, error message, no run.
- **A2** a requested split absent from the dataset → exit code 2 (the runner's fail-fast), not a
  silent zero-sample report.
- **A3** malformed `--class-map` or `--thresholds` → exit code 2.
- **A4** `vision` extra not installed → `--help` still works; a run fails with the import error.

## Acceptance criteria

- **AC1** One command (`make m3-report`, wrapping `scripts/vespai_baseline_report.py`) recomputes
  per-class precision / recall / F1 from the existing harness (`collect_samples` + `evaluate`),
  with no copy of the metric logic.
- **AC2** The detector runs **once** per invocation, with its confidence floor at the lowest
  reported threshold, and every reported threshold is scored from those samples; output is
  deterministic for the same inputs. (Floor 0 is not used: YOLOv5's CPU NMS then exceeds its time
  limit and drops boxes — observed on the first run.)
- **AC3** Defaults reproduce the committed report: splits `train valid test`, class map
  `0:vespa_crabro,1:vespa_velutina`, IoU 0.5, thresholds `0.5,0.8`.
- **AC4** A1–A3 exit with code 2 and an explicit message (unit-tested with fakes, no torch).
- **AC5** `docs/research/m3-vespai-baseline.md` records: the per-class numbers, dataset name /
  URL / version / licence (CC BY 4.0) / split sizes, weights provenance (file name, source,
  SHA-256, CC BY-NC-SA, loaded from a path, never committed), YOLOv5 commit, environment
  (Python, torch, OS, CPU/GPU), exact reproduction steps, and known limits (no bee class in this
  set → legal-floor not exercised).
- **AC6** No weights, dataset or images are committed; no heavy import enters `domain/` or
  `application/`.

## Out of scope

- Operating-point selection (M4, `measure_operating_point.py`), new datasets, the own model (M5),
  CI execution (weights are not in CI).

## UML

No flow change: the report reuses the M3 offline evaluation flow (runner → metrics). No new
diagram; no new port.
