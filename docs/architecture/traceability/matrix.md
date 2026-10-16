# Traceability matrix

Use case ↔ diagrams ↔ ADRs ↔ code ↔ tests. Feature `detection` drawn as-built on 2026-10-16.

| Use case | Diagrams | ADRs | Code | Tests |
|----------|----------|------|------|-------|
| UC1 Monitor the hive entrance for hornets | [use-case](../diagrams/detection/01-use-case.md), [sequence](../diagrams/detection/02-sequence-live-detection.md), [component](../diagrams/detection/03-component.md), [class](../diagrams/detection/04-class.md) | 0001, 0002, 0003, 0004, 0009 | `interface/cli/main.py`, `application/use_cases/detect_hornet_visual.py`, `application/decision.py`, `infrastructure/vision/` | `tests/unit/application/`, `tests/unit/interface/test_cli.py`, `tests/integration/test_vespai_detector.py` — spec [live-abstain](../specs/live-abstain.md) |
| UC2 Consult the detection log | use-case, sequence | 0006, 0009 | `infrastructure/notify/logging_notifier.py` | `tests/unit/infrastructure/test_logging_notifier.py` |
| UC3 Measure the detector on an annotated set | use-case, component | 0004 | `evaluation/runner.py`, `evaluation/metrics.py`, `evaluation/yolo.py` | `tests/unit/evaluation/` |
| UC4 Select the legal-floor operating point | use-case, component | 0003, 0004 | `evaluation/operating_point.py`, `scripts/measure_operating_point.py` | `tests/unit/evaluation/test_operating_point.py`, `tests/unit/scripts/test_measure_operating_point.py` |
| UC5 Deter an attacking hornet (planned) | use-case | 0005 | — | — |
