# State diagram — capture-rig — rig lifecycle

> **Feature**: capture-rig (brick C1) · **Spec**: [capture-rig](../../specs/capture-rig.md)

## Diagram

```mermaid
stateDiagram-v2
    [*] --> SelfCheck: power on / start
    SelfCheck --> Idle: checks done, outside daylight
    SelfCheck --> Recording: checks done, in daylight
    Idle --> SelfCheck: daylight window opens
    Recording --> Idle: daylight window closes

    state Recording {
        [*] --> Buffering
        Buffering --> SavingClip: motion in ROI
        SavingClip --> SavingClip: motion again (extend clip)
        SavingClip --> Buffering: 5 s post-roll elapsed or 5 min cap
    }

    Recording --> Degraded: one mic or camera lost
    Degraded --> Recording: device back
    Degraded --> Idle: daylight window closes
    Degraded --> Fault: all inputs lost
    Recording --> Fault: free space < 2 %
    Fault --> SelfCheck: retry every 60 s / Researcher action
```

## Notes

- *Degraded* follows the daylight window like *Recording*; the next window opens through
  *SelfCheck* again (*Idle* → *SelfCheck*), which re-detects a still-missing device and
  re-enters *Degraded*.
- *Degraded* keeps recording the remaining streams (spec A2, A3); the gap goes in the sidecars.
- Audio streams continuously in both *Buffering* and *SavingClip*.
- Power loss from any state restarts at *SelfCheck* (spec A5).
