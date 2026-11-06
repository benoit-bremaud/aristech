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
    UC->>CA: open(1080p30, ring 8 s, GOP 1 s)
    loop while in daylight window
        AU-->>UC: audio block (t_start from Clock)
        UC->>ST: append audio block
        alt 10-min boundary
            UC->>ST: close audio segment + sidecar
            opt free space < 10 %
                UC->>ST: delete oldest non-flagged
            end
        end
        CA-->>UC: motion latched (t_first), read at the next tick t_tick ≈ t_first + 1 s + tick work
        UC->>CA: save_clip(from t_tick − 8 s)
        Note over CA: ring from its first keyframe (5 s pre-roll + 3 s margin), then live frames
        CA-->>UC: motion ended (t_last)
        UC->>CA: stop_clip(at t_close = t_last + 5 s)
        Note over CA: the ring still flushes the clip's last frames for 8 s
        alt next clip opens at t_next < t_close + 8 s
            UC->>ST: clip sidecar, end = t_next − 8 s (its tail is the next clip's pre-roll)
        else 8 s elapse first
            UC->>ST: clip sidecar, end = t_close
        end
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
- A closed clip's sidecar waits one ring: if the next clip opens sooner (motion back within 8 s,
  or the 5 min cap during continuous motion), the camera closes the old file where the new one
  starts, so both sidecars meet at `t_next − 8 s` with no gap and no overlap (#178).
- Fault branches (mic, camera, disk) are in the [state diagram](04-state.md).
