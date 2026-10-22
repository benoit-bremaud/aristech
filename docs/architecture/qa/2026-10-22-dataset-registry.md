# QA — dataset registry, import, split, freeze (2026-10-22)

> **Scope**: `scripts/dataset.py` on branch `feat/dataset-registry-import-split`, run on the real
> Roboflow hornet-behavior export (364 images), with a scratch registry and store outside the
> repository. Spec `annotation-pipeline` AC1–AC5, A2–A5.

## Commands

```bash
python scripts/dataset.py --registry <scratch>/registry --store <scratch>/store \
  import --source roboflow-hornet-behavior-v1 --dir data/external/vespa-crabro-velutina \
  --class-map 0:1,1:0
python scripts/dataset.py --registry <scratch>/registry --store <scratch>/store split --seed 0
python scripts/dataset.py --registry <scratch>/registry --store <scratch>/store freeze --id test-v1
```

## Observed

| Check | Result |
|---|---|
| Import: 364 rows, 19 groups; manifest byte-identical to the committed one (AC2, AC4) | ✅ |
| Wrong class map `0:1` → exit 2 naming the label file (AC3, A4) | ✅ |
| `split --seed 0` → train 257, validation 44, test 63 (AC4) | ✅ |
| `freeze --id test-v1` → 63 images, sha256 `7f2a9b37…103bf`, label snapshot written (AC5) | ✅ |
| `split --seed 42` after freeze → exit 0, test-v1 groups stay in test (test 93) | ✅ |
| `freeze --id test-v1` again → exit 2 "already frozen" | ✅ |
| One snapshot label edited, then `split` → exit 2 "label snapshot … changed" (A5) | ✅ |

## Not covered

- Sledevic and iNaturalist sources (PR 3); C1 frames (2027 season, AC6 unit-tested only).
