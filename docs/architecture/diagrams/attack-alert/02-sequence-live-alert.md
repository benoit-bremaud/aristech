# Sequence diagram — attack-alert — one alert per episode in the live loop

> **Feature**: attack-alert (issue #149) · **Spec**: [attack-alert](../../specs/attack-alert.md) ·
> **ADRs**: ADR-0009, ADR-0031

## Diagram

```mermaid
sequenceDiagram
    participant UC as DetectHornetVisual
    participant V as VideoSource
    participant D as HornetDetector
    participant T as AttackEpisodeTracker
    participant N as Notifier

    loop every frame
        UC->>V: next frame
        V-->>UC: frame (video time or wall clock)
        UC->>D: detect(frame)
        D-->>UC: detections (≥ detector floor)
        loop every detection
            UC->>UC: decide(detection, ACT)
            alt ACT
                UC->>N: notify_detection
            else ABSTAIN
                UC->>N: notify_abstention
            end
        end
        UC->>T: observe(frame time, hit = any V. velutina ≥ COUNT)
        alt episode opens
            T-->>UC: episode (ended = None)
            UC->>N: notify_attack_started
        else episode closes
            T-->>UC: episode (ended set)
            UC->>N: notify_attack_ended
        else nothing
            T-->>UC: None
        end
    end
    UC->>V: close()
    UC->>T: close(last frame time)
    opt an episode was still open
        UC->>N: notify_attack_ended
    end
```

## Notes

- The ACT / ABSTAIN path is unchanged (ADR-0009); the episode path only reads the same detections.
- The detector floor must not exceed the COUNT point, or counted boxes would never reach the use
  case; the CLI enforces `floor ≤ COUNT ≤ ACT`.
