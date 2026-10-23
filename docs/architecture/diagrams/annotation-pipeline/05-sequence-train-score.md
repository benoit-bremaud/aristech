# Sequence diagram — export, train, score (UC9 + UC3)

> **Feature**: annotation-pipeline · **Spec**: [annotation-pipeline](../../specs/annotation-pipeline.md)
> (main scenario step 6, AC5, AC7, AC8, AC11) · **ADR**: ADR-0022, ADR-0024 · PR 4

```mermaid
sequenceDiagram
    actor R as Researcher
    participant CLI as dataset CLI (scripts/)
    participant Frz as frozen sets (test-v*)
    participant Exp as export_yolo_view
    participant Tr as train_rfdetr (scripts/, extra train)
    participant Rep as prefield_report (scripts/)
    participant RF as RFDETRDetector (infrastructure)
    participant VA as VespAIDetector (infrastructure)
    participant H as UC3 harness (collect_samples + evaluate)

    R->>R: check the 30-image box contact sheet (ADR-0024 D3)
    R->>CLI: export --out data/views/prefield
    CLI->>Frz: discover_frozen(registry) + violations(manifest rows)
    alt any violation or edited frozen file (A5)
        Frz-->>CLI: FrozenSetViolation / ValueError
        CLI-->>R: exit 2, nothing written
    end
    CLI->>Exp: rows, store, frozen sets
    Exp-->>R: data.yaml + train/ valid/ (links to the store) + test/ (frozen images, snapshot labels)
    R->>Tr: --view data/views/prefield --size small --epochs N
    Tr->>Tr: RFDETRSmall().train(dataset_dir=view) on train + valid only
    Tr-->>R: checkpoint (git-ignored) + its SHA-256
    R->>Rep: --view … --rfdetr-weights … --vespai-weights … --yolov5-dir …
    Rep->>Frz: load test-v1, its digest
    Rep->>RF: detect(frame) per test image
    Rep->>VA: detect(frame) per test image
    Rep->>H: samples of each detector, thresholds 0.5 and 0.8
    H-->>Rep: EvaluationReport per detector and threshold
    Rep-->>R: Markdown: per-class P/R side by side, manifest hash, test-v1 digest, weights hash, licences
```

## Notes

- The report never reads `train/` or `valid/`: only the frozen set's own folder.
- Both detectors run at the lowest threshold once; every threshold is scored from the same
  samples (as in the M3 report).
