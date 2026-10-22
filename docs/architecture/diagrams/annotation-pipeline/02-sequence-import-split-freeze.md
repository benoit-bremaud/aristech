# Sequence diagram — import, split, freeze

> **Feature**: annotation-pipeline · **Spec**: [annotation-pipeline](../../specs/annotation-pipeline.md)
> (main scenario steps 1–5, A2, A3, A4, A5) · as built in PR 2 (`scripts/dataset.py`)

```mermaid
sequenceDiagram
    actor R as Researcher
    participant CLI as dataset CLI (scripts/)
    participant Reg as registry (load_register / require)
    participant Imp as import_yolo_source
    participant Man as manifest (merge_rows, CSV)
    participant Spl as split_by_group
    participant Frz as frozen sets (test-v*)

    R->>CLI: import --source roboflow-hornet-behavior-v1 --dir data/external/... --class-map 0:1,1:0
    CLI->>Reg: require(sources, source)
    alt unknown source or licence not in allow-list (A2)
        Reg-->>CLI: LicenceError
        CLI-->>R: exit 2
    end
    CLI->>Imp: images + labels + class map
    alt unmapped source class (A4)
        Imp-->>CLI: ValueError(label file: unmapped)
        CLI-->>R: exit 2
    end
    Imp-->>Man: rows (image sha256, source, group, label sha256, classes)
    Man->>Man: merge with existing rows, join groups sharing an image (A3)
    R->>CLI: split --seed 0
    CLI->>Frz: discover_frozen(registry): load + verify digest and label snapshot
    alt frozen file, digest or snapshot edited
        Frz-->>CLI: ValueError
        CLI-->>R: exit 2
    end
    CLI->>Spl: manifest rows, every frozen set
    Spl->>Frz: violations(assignment)
    alt frozen image moved / label changed / frozen group in train or validation (A5)
        Frz-->>CLI: FrozenSetViolation
        CLI-->>R: exit 2 + offending images
    end
    Spl-->>Man: split column
    R->>CLI: freeze --id test-v1
    alt version exists
        CLI-->>R: exit 2 (never rewritten)
    end
    CLI->>Frz: test rows + label snapshot (staged, renamed) + test-v1.sha256
    CLI-->>R: frozen set id + hash
```
