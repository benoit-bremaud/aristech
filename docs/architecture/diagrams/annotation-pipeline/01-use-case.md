# Use-case diagram — annotation-pipeline

> **Feature**: annotation-pipeline (issue #95) · **Spec**: [annotation-pipeline](../../specs/annotation-pipeline.md)
> **Related ADRs**: ADR-0015, ADR-0018 to ADR-0022

## Context

UC8 is refined into three actor goals. Hashing, class mapping and leakage checks are system
behaviour inside them, not use cases. UC9 includes UC3 (score on the frozen set).

## Diagram

```mermaid
flowchart LR
    Researcher(("Researcher"))
    Publisher(("Public dataset publisher"))
    Rig(("Capture rig C1"))
    subgraph data["Dataset domain"]
        UC8(["UC8 Annotate images for the database"])
        UC8a(["UC8a Register a source and its licence"])
        UC8b(["UC8b Import and annotate images"])
        UC8c(["UC8c Freeze the test set"])
    end
    subgraph model["Model domain"]
        UC9(["UC9 Train and compare an own detector"])
        UC3(["UC3 Measure a detector on an annotated set"])
    end
    Researcher --- UC8a
    Researcher --- UC8b
    Researcher --- UC8c
    Researcher --- UC9
    Publisher --- UC8a
    Rig --- UC8b
    UC8 -. "include" .-> UC8a
    UC8 -. "include" .-> UC8b
    UC8 -. "include" .-> UC8c
    UC9 -. "include" .-> UC3
```

## Notes

- The publisher and C1 are secondary actors: they supply images and metadata, they initiate nothing.
- UC8c happens once per test-set version (`test-v1` public, `test-v2` adds field groups).
