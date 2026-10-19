# ADR-0018: X-AnyLabeling as annotation tool, YOLO txt as canonical label format

- Status: Proposed
- Date: 2026-10-19 (issue #95, spec annotation-pipeline)

## Context

UC8 needs a small annotation tool with model pre-annotation (human-corrected) and one canonical,
open label format. The harness already parses YOLO txt (`evaluation/yolo.py`); the Roboflow set
and the Sledevic bee set (CC BY 4.0, verified) ship YOLO txt. labelImg is archived (2024-02-29).

## Options (MCDA)

Script: [`mcda/adr_0018_0022_annotation_pipeline.py`](mcda/adr_0018_0022_annotation_pipeline.py). Scores 0–5, weights /100, totals /500; scores are estimates unless marked verified.

| Option | Licence 15 | Pre-annotation 25 | Setup 20 | Format fit 25 | Longevity 15 | Total |
|---|---|---|---|---|---|---|
| A. CVAT (MIT, Docker server) + YOLO txt | 5 | 4 | 2 | 5 | 5 | 415 |
| B. Label Studio (Apache-2.0) + COCO JSON | 5 | 3 | 3 | 3 | 4 | 345 |
| C. X-AnyLabeling (GPL-3.0 desktop) + YOLO txt | 4 | 5 | 5 | 5 | 3 | **455** |
| D. labelImg + YOLO txt | 5 | 0 | 5 | 4 | 0 | 275 |

Sensitivity: longevity 30 → A 440, C 425 (A leads); licence 30 → C 440, A 435; pre-annotation 35 →
C 455, A 435. **Fragile between A and C**; the choice is reversible because the format (YOLO txt)
is the contract, not the tool.

## Decision

- Canonical labels: **YOLO txt**, one file per image, class ids fixed:
  `0 vespa_velutina, 1 vespa_crabro, 2 apis_mellifera, 3 other`. Source class ids are remapped at
  import (explicit map, unmapped class = error).
- Tool: **X-AnyLabeling** (local, ONNX pre-annotation with our own model once trained). The tool's
  GPL applies to the tool only, not to the data or the model. CVAT stays the fallback.
- A converter to COCO JSON is written only if the training stack requires it (ADR-0022).

## Consequences

- No server to run; annotation stays on the owner's machine.
- If X-AnyLabeling stalls, switching to CVAT costs nothing on the data side.
