# Class diagram — dataset module

> **Feature**: annotation-pipeline · **Spec**: [annotation-pipeline](../../specs/annotation-pipeline.md)

## Context

Stdlib-only code in `src/aristech/datasets/` (beside `distribute.py`), like `evaluation/`: an
offline tool, not runtime detection, so no port (no second implementation, ADR-0010). It reuses
the domain `Species` for the four classes (`UNKNOWN` = "other"). Training lives outside the
package (ADR-0022).

## Diagram

```mermaid
classDiagram
    class Licence {
        <<enumeration>>
        CC_BY_4_0
        CC_BY_SA_4_0
        CC0_1_0
        OWN
    }
    class Source {
        +id: str
        +name: str
        +url: str
        +version: str
        +licence: Licence
        +attribution: str
        +retrieved: date
        +captive: bool
    }
    class LicenceRegister {
        +sources: dict~str, Source~
        +require(source_id) Source
    }
    class ManifestRow {
        +image_sha256: str
        +source_id: str
        +source_path: str
        +group: str
        +label_sha256: str
        +classes: frozenset~Species~
        +split: Split
    }
    class Split {
        <<enumeration>>
        TRAIN
        VALIDATION
        TEST
        UNASSIGNED
    }
    class FrozenTestSet {
        +id: str
        +rows: tuple~ManifestRow~
        +digest() str
        +violations(rows) list~str~
    }
    LicenceRegister "1" o-- "*" Source
    Source --> Licence
    ManifestRow --> Split
    ManifestRow ..> Source : source_id
    FrozenTestSet "1" o-- "*" ManifestRow
```

## Notes

- `split_by_group(rows, seed, ratios, frozen)` and `group_for_capture(metadata)` are functions,
  not classes (KISS).
- Licence ids follow SPDX.
