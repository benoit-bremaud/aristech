# QA — dataset registry, import, split, freeze (2026-10-22)

Branch `feat/dataset-registry-import-split`, spec `annotation-pipeline` AC1–AC5. Run on the real
Roboflow hornet-behavior export (364 images), in a scratch registry and store outside the repo.

| Step | Command | Expected | Result |
|---|---|---|---|
| Import | `import --source roboflow-hornet-behavior-v1 --dir … --class-map 0:1,1:0` | 364 rows, 19 groups | OK; manifest byte-identical to the committed one |
| Wrong class map | `import … --class-map 0:1` | exit 2, label file named | OK |
| Split | `split --seed 0` | train 257 / validation 44 / test 63 | OK |
| Freeze | `freeze --id test-v1` | 63 images + digest + label snapshot | OK, sha256 `7f2a9b37…103bf` |
| Re-split, other seed | `split --seed 42` | exit 0, test-v1 groups kept in test | OK (test 93, train 228, validation 43) |
| Re-freeze same id | `freeze --id test-v1` | exit 2, "already frozen" | OK |
| Tampered snapshot | append a line to one `test-v1-labels/*.txt`, then `split` | exit 2, "label snapshot … changed" | OK |

Unit tests: 222 passed, 2 skipped; coverage manifest 100 %, registry 100 %, split 98 %.
