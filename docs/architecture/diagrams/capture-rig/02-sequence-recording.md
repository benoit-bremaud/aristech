# Sequence diagram — capture-rig — synchronised recording

> **Feature**: capture-rig (brick C1) · **Spec**: [capture-rig](../../specs/capture-rig.md)
> **Related ADRs**: ADR-0017

## Context

One daylight window: both audio channels stream continuously; video frames fill a RAM ring
buffer and a motion event saves pre-roll + live frames. Every timestamp comes from one
`Clock` (monotonic, mapped to UTC once per segment), which is what makes AC1 testable.

## Diagram

```mermaid
sequenceDiagram
    autonumber
    actor R as Researcher
    participant UC as RecordCampaign (application)
    participant CK as Clock (port)
    participant AU as AudioRecorder (port)
    participant CA as CameraRecorder (port)
    participant ST as SegmentStore (port)

    R->>UC: start(campaign config)
    UC->>CK: now(), source()
    UC->>AU: open(2 ch, 48 kHz)
    UC->>CA: open(1080p30, ring 10 s)
    loop while in daylight window
        AU-->>UC: audio block (t_start from Clock)
        UC->>ST: append audio block
        alt 10-min boundary
            UC->>ST: close audio segment + sidecar
            opt free space < 10 %
                UC->>ST: delete oldest non-flagged
            end
        end
        CA-->>UC: motion event (t_first)
        UC->>CA: save_clip(from t_first − 5 s)
        Note over CA: pre-roll from ring buffer, then live frames
        CA-->>UC: motion ended (t_last)
        UC->>CA: stop_clip(at t_last + 5 s)
        UC->>ST: store clip + sidecar (same clock)
        opt free space < 10 %
            UC->>ST: delete oldest non-flagged
        end
    end
    UC->>AU: close()
    UC->>CA: close()
    UC->>ST: close open segment + sidecar
```

## Notes

- The free-space check runs after every closed audio segment and every stored clip, so audio
  alone (no motion) still triggers rotation (spec A1).
- Fault branches (mic, camera, disk) are in the [state diagram](04-state.md).
