# Component diagram — capture-rig

> **Feature**: capture-rig (brick C1) · **Related ADRs**: ADR-0001, ADR-0010, ADR-0017

## Context

The recording logic (daylight window, pre/post-roll, rotation, faults) lives in `application/`
and is unit-tested with hand-written fakes. Hardware libraries (Picamera2, sounddevice,
soundfile) live in `infrastructure/capture/` behind the optional `capture` extra. The ports are
justified by a present force (ADR-0010): each has a real adapter **and** a test fake.

## Diagram

```mermaid
flowchart TB
    subgraph interface["interface"]
        CLI["cli/record.py — composition root (aristech-record)"]
    end
    subgraph application["application"]
        RC["use_cases/RecordCampaign"]
        P_CA[["port CameraRecorder"]]
        P_AU[["port AudioRecorder"]]
        P_ST[["port SegmentStore"]]
        P_CK[["port Clock"]]
    end
    subgraph domain["domain"]
        DOM["SegmentMetadata, DaylightWindow, RigFault"]
    end
    subgraph infrastructure["infrastructure/capture (extra: capture)"]
        PIC["Picamera2Recorder (ring buffer + motion)"]
        ALSA["SoundDeviceRecorder (I²S, 2 ch → FLAC)"]
        FS["FileSegmentStore (SSD + JSON sidecars)"]
        SYS["SystemClock (monotonic → UTC, NTP/RTC)"]
    end
    CLI --> RC
    CLI --> PIC & ALSA & FS & SYS
    RC --> P_CA & P_AU & P_ST & P_CK
    RC --> DOM
    PIC -. implements .-> P_CA
    ALSA -. implements .-> P_AU
    FS -. implements .-> P_ST
    SYS -. implements .-> P_CK
```

## Notes

- No dependency from `capture` to `vision`: the collector never runs a detector (neutral rig).
