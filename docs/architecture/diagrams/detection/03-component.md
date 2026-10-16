# Component diagram — detection — layers and ports (as-built)

> **Feature**: detection v1
> **Related ADRs**: ADR-0001, ADR-0002, ADR-0006

## Context

Structural boundaries of the detection path and the offline evaluation, with the dependency rule
(arrows point to what a component depends on). Speculative ports with no consumer (audit S1) were
removed in brick B5 (ADR-0010).

## Diagram

```mermaid
flowchart TB
    subgraph interface["interface"]
        CLI["cli/main.py — composition root"]
    end
    subgraph application["application"]
        UC["use_cases/DetectHornetVisual"]
        DEC["decision.decide()"]
        P_VS[["port VideoSource"]]
        P_DET[["port HornetDetector"]]
        P_N[["port Notifier"]]
    end
    subgraph domain["domain"]
        DOM["Detection, Species, BoundingBox, VideoFrame"]
    end
    subgraph infrastructure["infrastructure (extra: vision)"]
        CV["vision/OpenCVVideoSource"]
        VESP["vision/VespAIDetector"]
        LOG["notify/LoggingNotifier"]
    end
    subgraph evaluation["evaluation (offline, lazy cv2)"]
        RUN["runner.evaluate_on_dataset"]
        OP["operating_point.select_operating_point"]
        MET["metrics (IoU, matching, per-class report)"]
    end
    EXT[("VespAI weights + YOLOv5 repo — operator-supplied, CC BY-NC-SA")]

    CLI --> UC
    CLI --> CV
    CLI --> VESP
    CLI --> LOG
    UC --> DEC
    UC --> P_VS
    UC --> P_DET
    UC --> P_N
    DEC --> DOM
    CV -. implements .-> P_VS
    VESP -. implements .-> P_DET
    LOG -. implements .-> P_N
    VESP --> EXT
    RUN --> P_DET
    RUN --> MET
    OP --> MET
    application --> domain
    evaluation --> domain
```

## Notes

- `domain/` imports nothing outside itself; `application/` imports only `domain/`; torch, cv2 and
  YOLOv5 stay in `infrastructure/` or behind a lazy import (`evaluation/runner.py`).
- `HornetDetector` has two consumers (live use case, offline evaluation): the force that
  justifies the port.
- The legacy Keras `training/` package was removed in B5 (ADR-0010). Its generic file splitter
  survives as `aristech.datasets.distribute`, a stdlib-only helper used by the dataset scripts,
  outside the detection path.
