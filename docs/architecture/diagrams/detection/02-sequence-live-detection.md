# Sequence diagram — detection — UC1 live detection loop (as-built)

> **Feature**: detection v1
> **Source**: `src/aristech/interface/cli/main.py`, `src/aristech/application/use_cases/detect_hornet_visual.py`,
> `src/aristech/application/decision.py`
> **Related ADRs**: ADR-0001, ADR-0003, ADR-0004

## Context

What happens in time when the operator runs UC1. Drawn as-built to make the double confidence
filter visible (audit finding M3), which brick B4 fixes.

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

    Operator->>CLI: run with --video, --weights, --yolov5-dir, --confidence c
    CLI->>CLI: validate arguments (exit 2 on error)
    CLI->>VS: create(source — camera index or file path)
    CLI->>DET: create with confidence = c
    CLI->>UC: create with confidence_threshold = c
    CLI->>UC: run()
    UC->>VS: frames()
    loop each VideoFrame yielded
        VS-->>UC: VideoFrame
        UC->>DET: detect(frame)
        Note over DET: drops every box below c (first filter)
        DET-->>UC: detections with confidence >= c
        loop each detection
            UC->>DEC: decide(detection, c)
            Note over DEC: second filter at the same c — ABSTAIN is unreachable
            alt V. velutina and confidence >= c
                DEC-->>UC: ACT
                UC->>N: notify_detection(detection)
            else V. velutina and confidence < c (unreachable today)
                DEC-->>UC: ABSTAIN
            else other species
                DEC-->>UC: IGNORE
            end
        end
    end
    UC->>VS: close()
    UC-->>CLI: accepted detections
    CLI-->>Operator: log count, exit 0
```

## Notes

- The ABSTAIN branch of `decide()` exists and is unit-tested, but never fires in the live path
  because the detector already dropped every box below `c` (audit M3, ADR-0004 consequences).
- Fix direction for B4: the detector runs at a low floor and only `decide()` applies the
  operating threshold, so uncertain targets are visible as ABSTAIN.
- `close()` runs in a `finally`, also on detector errors.
