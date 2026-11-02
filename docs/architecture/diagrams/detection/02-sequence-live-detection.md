# Sequence diagram — detection — UC1 live detection loop

> **Feature**: detection v1
> **Source**: `src/aristech/interface/cli/main.py`, `src/aristech/application/use_cases/detect_hornet_visual.py`,
> `src/aristech/application/decision.py`,
> `src/aristech/infrastructure/vision/rfdetr_detector.py`
> **Related ADRs**: ADR-0001, ADR-0003, ADR-0004, ADR-0009, ADR-0029, ADR-0030
> **Spec**: `docs/architecture/specs/live-abstain.md`

## Context

What happens in time when the operator runs UC1. Since brick B4 (ADR-0009) the detector runs at a
low floor `f` and only `decide()` applies the operating threshold `c`, so uncertain targets are
reported as abstentions instead of vanishing (audit M3, now fixed). Since #140 (ADR-0030) the
operator picks the detector, and every run logs FPS and latency.

## Diagram

```mermaid
sequenceDiagram
    actor Operator
    participant CLI as cli main (composition root)
    participant UC as DetectHornetVisual
    participant VS as OpenCVVideoSource (VideoSource)
    participant T as _TimedDetector (HornetDetector)
    participant DET as RFDETRDetector or VespAIDetector (HornetDetector)
    participant DEC as decide()
    participant N as LoggingNotifier (Notifier)

    Operator->>CLI: run with --video, --detector d, --checkpoint or --weights/--yolov5-dir, [--confidence c], [--detector-floor f]
    CLI->>CLI: c defaults to 0.45 (rfdetr) or 0.5 (vespai); validate 0 <= f <= c <= 1 (exit 2 on error)
    opt d = rfdetr
        CLI->>CLI: sha256(checkpoint) != ADR-0029 model → warn "not a measured ACT point"
    end
    CLI->>VS: create(source — camera index or file path)
    CLI->>DET: create with confidence = f
    CLI->>T: wrap(DET)
    CLI->>UC: create with confidence_threshold = c
    CLI->>UC: run()
    UC->>VS: frames()
    loop each VideoFrame yielded
        VS-->>UC: VideoFrame
        UC->>T: detect(frame)
        T->>DET: detect(frame) — latency recorded
        Note over DET: drops boxes below the floor f only
        DET-->>T: detections with confidence >= f
        T-->>UC: detections
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
                UC->>UC: log debug "ignore"
            end
        end
    end
    UC->>VS: close()
    UC-->>CLI: DetectionRun(threats, abstentions)
    CLI-->>Operator: log FPS, latency p50/p95 and both counts, exit 0
```

## Notes

- `--detector-floor` defaults to 0.1, lowered to `c` when `c < 0.1`.
- The first `detect` loads the model; it is logged as warm-up, outside the FPS figures.
- Other species are never reported, neither as threat nor as abstention (legal floor, ADR-0003); they
  are logged at debug level only.
- `close()` runs in a `finally`, also on detector errors.
