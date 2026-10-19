# Use-case diagram — product — target goals after the needs brainstorm

> **Feature**: product scope re-targeted 2026-10-16
> **Source specs**: `attack-alert`, `capture-rig`, `own-vision-model`, `acoustic-feasibility`,
> `deterrence-field-test`; `docs/requirements.md`
> **Related ADRs**: ADR-0003, ADR-0005, ADR-0013, ADR-0014, ADR-0015, ADR-0016

## Context

The target set of actor goals, extending the as-built detection diagram
(`../detection/01-use-case.md`, UC1–UC5). Planned goals are marked. Grouped by domain, not by
component.

## Diagram

```mermaid
flowchart LR
    Beekeeper["Beekeeper — owns the hives"]
    Researcher["Researcher — collects data, trains and calibrates"]

    subgraph System["aristech"]
        subgraph Monitoring
            UC1(["UC1 Monitor the hive entrance for hornets"])
            UC2(["UC2 Consult the detection log"])
            UC6(["UC6 Respond to an ongoing hornet attack (planned)"])
        end
        subgraph Data
            UC7(["UC7 Record synchronised field footage (planned, C1)"])
            UC8(["UC8 Annotate images for the database (planned)"])
        end
        subgraph Calibration
            UC3(["UC3 Measure the detector on an annotated set"])
            UC4(["UC4 Select the operating points"])
            UC9(["UC9 Train and compare an own detector (planned, M5)"])
            UC10(["UC10 Assess the acoustic signal (planned, A0)"])
        end
        subgraph Deterrence
            UC5(["UC5 Deter an attacking hornet (planned, gated by D0)"])
        end
    end

    Beekeeper --- UC1
    Beekeeper --- UC2
    Beekeeper --- UC6
    Researcher --- UC7
    Researcher --- UC8
    Researcher --- UC3
    Researcher --- UC4
    Researcher --- UC9
    Researcher --- UC10
    UC4 -. "«include»" .-> UC3
    UC9 -. "«include»" .-> UC3
    UC10 -. "«include»" .-> UC8
    UC6 -. "«extend» (attack episode opens)" .-> UC1
    UC5 -. "«extend» (on ACT decision)" .-> UC1
```

## Notes

- The detection diagram calls the beekeeper "Operator"; same actor.
- UC4 now selects **two** points (ACT, COUNT — ADR-0014); the as-built one selects ACT only.
- UC6 is the beekeeper's goal (react to the attack); the alert is its trigger, not a use case.
- D0 is a manual field protocol (spec `deterrence-field-test`), not a system use case; it gates UC5.
- UC10's outcome may add an acoustic input to UC1; it can only reinforce abstention (ADR-0016).
