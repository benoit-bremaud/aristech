# Traceability matrix

Use case ↔ diagrams ↔ ADRs ↔ code ↔ tests. Feature `detection` drawn as-built on 2026-10-16; planned UC6–UC10 added by the needs brainstorm of 2026-10-16 (ADR-0013 to ADR-0016); updated for brick B4 (ADR-0009) and B5 (ADR-0010) and B7 (ADR-0012, `vision` extra bounds; Dependabot holds the numpy 2 / opencv 5 majors, spec [dependabot-major-holds](../specs/dependabot-major-holds.md)).

| Use case | Diagrams | ADRs | Code | Tests |
|----------|----------|------|------|-------|
| UC1 Monitor the hive entrance for hornets | [use-case](../diagrams/detection/01-use-case.md), [sequence](../diagrams/detection/02-sequence-live-detection.md), [component](../diagrams/detection/03-component.md), [class](../diagrams/detection/04-class.md) | 0001, 0002, 0003, 0004, 0009, 0012; planned changes: 0014 (two points), 0015 (own model), 0016 (audio) | `interface/cli/main.py`, `application/use_cases/detect_hornet_visual.py`, `application/decision.py`, `infrastructure/vision/` | `tests/unit/application/`, `tests/unit/interface/test_cli.py`, `tests/unit/interface/test_cli_wiring.py`, `tests/integration/test_vespai_detector.py` — spec [live-abstain](../specs/live-abstain.md); VespAI load on the locked torch: spec [dependabot-relock](../specs/dependabot-relock.md) |
| UC2 Consult the detection log | use-case, sequence | 0006, 0009, 0013 | `infrastructure/notify/logging_notifier.py` | `tests/unit/infrastructure/test_logging_notifier.py` |
| UC3 Measure the detector on an annotated set | use-case, component | 0004 | `evaluation/runner.py`, `evaluation/metrics.py`, `evaluation/yolo.py` | `tests/unit/evaluation/` |
| UC4 Select the operating points (as-built: ACT only; COUNT planned) | use-case, component, [product use-case](../diagrams/product/01-use-case.md) | 0003, 0004, 0014 | `evaluation/operating_point.py`, `scripts/measure_operating_point.py` | `tests/unit/evaluation/test_operating_point.py`, `tests/unit/scripts/test_measure_operating_point.py` |
| UC5 Deter an attacking hornet (planned) | use-case, product use-case | 0003, 0005 | — | — (spec [deterrence-field-test](../specs/deterrence-field-test.md), D0) |
| UC6 Respond to an ongoing hornet attack (planned) | [product use-case](../diagrams/product/01-use-case.md), [data-flow](../diagrams/product/02-data-flow.md) | 0013, 0014 | — | — (spec [attack-alert](../specs/attack-alert.md)) |
| UC7 Record synchronised field footage (planned) | product use-case, data-flow, [capture-rig](../diagrams/capture-rig/) (use-case, sequence, component, state) | 0015, 0016, 0017 | — | — (spec [capture-rig](../specs/capture-rig.md)) |
| UC8 Annotate field recordings (planned) | product use-case, data-flow | 0015 | — | — (spec [own-vision-model](../specs/own-vision-model.md)) |
| UC9 Train and compare an own detector (planned) | product use-case, data-flow | 0015, 0014 | — | — (spec [own-vision-model](../specs/own-vision-model.md)) |
| UC10 Assess the acoustic signal (planned) | product use-case, data-flow | 0016 | — | — (spec [acoustic-feasibility](../specs/acoustic-feasibility.md)) |
