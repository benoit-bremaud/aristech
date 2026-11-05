# Sequence diagram — health-push — heartbeat and faults in the live loop

> **Feature**: health-push (issue #158) · **Spec**: [health-push](../../specs/health-push.md) ·
> **ADRs**: ADR-0032, ADR-0033

## Diagram

```mermaid
sequenceDiagram
    participant UC as DetectHornetVisual
    participant V as VideoSource
    participant H as HealthMonitor
    participant C as Clock
    participant N as Notifier (TelegramNotifier → LoggingNotifier)
    participant P as Telegram Bot API

    loop every frame
        UC->>V: next frame
        Note over UC: detect, decide, episodes (attack-alert sequence)
        UC->>H: tick(frames, episodes)
        H->>C: now()
        alt heartbeat due
            H-->>UC: Heartbeat
            UC->>N: notify_heartbeat
            N->>P: sendMessage "Unit alive …"
        else not due
            H-->>UC: None
        end
    end
    alt live source ended
        UC->>H: fault(source_ended)
    else loop raised an error
        UC->>H: fault(loop_error, error type)
    end
    alt outside the cool-down
        H-->>UC: Fault (with muted count)
        UC->>N: notify_fault
        N->>P: sendMessage "Unit fault …" (queued as [delayed] if the channel is down)
    else muted
        H-->>UC: None
    end
    Note over UC: on error: close the open episode and the source, then raise
```

## Notes

- The clock is the wall clock, never the video time (AC1); a hung source stops the heartbeat,
  which is the signal (A4).
