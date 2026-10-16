# Class diagram — detection — domain and decision types (as-built)

> **Feature**: detection v1
> **Source**: `src/aristech/domain/`, `src/aristech/application/decision.py`,
> `src/aristech/application/ports/`
> **Related ADRs**: ADR-0003, ADR-0004

## Context

The entities exchanged on the detection path and the decision vocabulary. Types used only by the
speculative ports (`Target`, `Point3D`, `AudioSample`) were removed in B5 (ADR-0010).

## Diagram

```mermaid
classDiagram
    class Species {
        <<enumeration>>
        VESPA_VELUTINA
        VESPA_CRABRO
        APIS_MELLIFERA
        UNKNOWN
    }
    class BoundingBox {
        +float x
        +float y
        +float width
        +float height
        +center: Point2D readOnly
        +area: float readOnly
    }
    class Point2D {
        +float x
        +float y
    }
    class VideoFrame {
        +pixels
        +int width
        +int height
        +datetime timestamp
    }
    class Detection {
        +Species species
        +BoundingBox bbox
        +float confidence
        +datetime timestamp
        +is_hornet() bool
        +is_threat() bool
    }
    class decision {
        <<utility>>
        +decide(detection Detection, threshold float) Decision
    }
    class Decision {
        <<enumeration>>
        ACT
        ABSTAIN
        IGNORE
    }
    class HornetDetector {
        <<interface>>
        +detect(frame VideoFrame) Sequence~Detection~
    }
    class VideoSource {
        <<interface>>
        +frames() Iterator~VideoFrame~
        +close()
    }
    class Notifier {
        <<interface>>
        +notify_detection(detection Detection)
        +notify_abstention(detection Detection)
    }

    Detection --> Species
    Detection *-- BoundingBox
    BoundingBox ..> Point2D
    HornetDetector ..> VideoFrame
    HornetDetector ..> Detection
    VideoSource ..> VideoFrame
    Notifier ..> Detection
    decision ..> Detection
    decision ..> Decision
```

## Notes

- All domain types are frozen dataclasses; `Detection` rejects a confidence outside [0, 1].
- `is_threat()` is true only for *V. velutina*; `is_hornet()` also includes *V. crabro*, which is
  never acted upon (`decide()` returns IGNORE).
- `decide()` is a pure function in `application/`; moving it to `domain/` is an audit Nice (N1).
- No state diagram: `Decision` is a stateless mapping, no object has a lifecycle on this path.
- No data-flow diagram: the path processes no personal data.
