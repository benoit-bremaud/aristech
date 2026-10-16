# Data-flow diagram — product — the field-data flywheel

> **Feature**: product scope re-targeted 2026-10-16
> **Source specs**: `capture-rig`, `own-vision-model`, `acoustic-feasibility`, `attack-alert`
> **Related ADRs**: ADR-0013, ADR-0014, ADR-0015, ADR-0016

## Context

How field recordings become the own model and the operating points, and how the deployed model
feeds back new footage. Planned flows; nothing here is implemented yet.

## Diagram

```mermaid
flowchart LR
    Hive(("Hive entrance"))
    Rig["C1 capture rig<br/>video + 2 mics, one clock"]
    Raw[("Raw segments<br/>+ metadata")]
    Public[("Public data<br/>CC BY / CC0 only")]
    Annot["UC8 annotation<br/>pre-label + human fix"]
    Train[("Training split")]
    Test[("Frozen test set<br/>split by day / hive")]
    Fit["UC9 fine-tune<br/>permissive base"]
    Eval["UC3 / UC4 harness<br/>per-class, ACT + COUNT points"]
    Model["Own detector<br/>HornetDetector adapter"]
    A0["UC10 A0 acoustic<br/>analysis"]
    Live["UC1 live monitoring"]
    Log[("Detection log<br/>+ evidence clips")]
    Alert["UC6 attack alert"]

    Hive --> Rig --> Raw --> Annot
    Public --> Annot
    Annot --> Train --> Fit --> Model
    Annot --> Test --> Eval
    Model --> Eval
    Annot --> A0
    Eval -- "thresholds" --> Live
    Model --> Live
    Live --> Log
    Live --> Alert
    Log -- "new footage" --> Annot
```

## Notes

- The frozen test set never feeds training; it is versioned and only grows by explicit decision.
- Every item in Public carries its licence; NC sources are excluded (ADR-0015).
- VespAI is evaluated on the same frozen set as the baseline.
