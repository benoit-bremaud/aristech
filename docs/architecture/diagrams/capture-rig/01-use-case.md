# Use-case diagram — capture-rig

> **Feature**: capture-rig (brick C1) · **Spec**: [capture-rig](../../specs/capture-rig.md)
> **Related ADRs**: ADR-0015, ADR-0016, ADR-0017

## Context

The capture rig serves one actor-initiated goal, UC7, refined into its sub-goals. Motion
triggers, the daylight window and the disk watchdog are system behaviour inside UC7, not use cases.

## Diagram

```mermaid
flowchart LR
    Researcher(("Researcher"))
    Beekeeper(("Beekeeper"))
    subgraph capture["Capture domain"]
        UC7(["UC7 Record synchronised field footage"])
        UC7a(["UC7a Install and start a campaign"])
        UC7b(["UC7b Check the rig's health"])
        UC7c(["UC7c Collect the recorded segments"])
    end
    Researcher --- UC7a
    Researcher --- UC7b
    Researcher --- UC7c
    Beekeeper --- UC7
    UC7 -. "include" .-> UC7a
    UC7 -. "include" .-> UC7c
    UC7b -. "extend (on fault)" .-> UC7
```

## Notes

- UC7b reads the fault log and the last sidecars (home: over Wi-Fi; remote: at the visit).
- The Beekeeper only hosts the rig (secondary actor).
