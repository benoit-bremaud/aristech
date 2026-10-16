# Sequence diagram — detection — UC1 live detection loop

> **Feature**: detection v1
> **Source**: `src/aristech/interface/cli/main.py`, `src/aristech/application/use_cases/detect_hornet_visual.py`,
> `src/aristech/application/decision.py`
> **Related ADRs**: ADR-0001, ADR-0003, ADR-0004, ADR-0009
> **Spec**: `docs/architecture/specs/live-abstain.md`

## Context

What happens in time when the operator runs UC1. Since brick B4 (ADR-0009) the detector runs at a
low floor `f` and only `decide()` applies the operating threshold `c`, so uncertain targets are
reported as abstentions instead of vanishing (audit M3, now fixed).

## Diagram

```mermaid
sequenceDiagram
    actor Operator
    participant CLI as cli main (composition root)
    participant UC as DetectHornetVisual
    participant VS as OpenCVVideoSource (VideoSource)
    participant DET as VespAIDetector (HornetDetector)
    participant DEC as decide()
    participant N as LoggingNotifier (Notifier)

    Operator->>CLI: run with --video, --weights, --yolov5-dir, --confidence c, --detector-floor f
    CLI->>CLI: validate arguments, require 0 <= f <= c <= 1 (exit 2 on error)
    CLI->>VS: create(source — camera index or file path)
    CLI->>DET: create with confidence = f
    CLI->>UC: create with confidence_threshold = c
    CLI->>UC: run()
    UC->>VS: frames()
    loop each VideoFrame yielded
        VS-->>UC: VideoFrame
        UC->>DET: detect(frame)
        Note over DET: drops boxes below the floor f only
        DET-->>UC: detections with confidence >= f
        loop each detection
            UC->>DEC: decide(detection, c)
            alt V. velutina and confidence >= c
                DEC-->>UC: ACT
                UC->>N: notify_detection(detection)
            else V. velutina and f <= confidence < c
                DEC-->>UC: ABSTAIN
                UC->>N: notify_abstention(detection)
            else other species
                DEC-->>UC: IGNORE
            end
        end
    end
    UC->>VS: close()
    UC-->>CLI: DetectionRun(threats, abstentions)
    CLI-->>Operator: log both counts, exit 0
```

## Notes

- `--detector-floor` defaults to 0.1, lowered to `c` when `c < 0.1`.
- Other species are never reported, neither as threat nor as abstention (legal floor, ADR-0003).
- `close()` runs in a `finally`, also on detector errors.
