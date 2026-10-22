# QA — annotation pipeline PR 3 (Sledevic + iNaturalist + test-v1), 2026-10-22

No UI: this pass runs the documented commands on the real data and checks their outputs.
Pixels stay in the git-ignored `data/external/`; only registry text files are committed.

## Sledevic bee detection v6 (CC BY 4.0, DOI 10.17632/8gb9r2yhfc.6)

- Fetched through the Mendeley public API with no login (`docs/architecture/qa/tools/sledevic_sample.py`).
  Every file is checked against its published SHA-256.
- Evenly spaced sample of at most 188 labelled frames per landing board. Files are renamed
  `<hive>_<frame>` so the `video` group rule gives one group per board.
- Frames per board: 20230609a 188 · 20230609b 188 · 20230609c 188 · 20230609d 188 ·
  20230609e 152 · 20230711a 188 · 20230711b 188 · 20230711c 173. Total **1,453**.
- Imported with class map bees → 2 (apis_mellifera): 10,033 boxes.

## iNaturalist (CC BY / CC0 research grade, ADR-0023)

- `scripts/inat_fetch.py` fetched 450 photos for velutina, crabro and "other" taxa. Each has a
  row in `data/registry/inat-attribution.csv`, excluded photos included.
- Pre-annotation (`docs/architecture/qa/tools/preannotate.py`):
  - model Grounding DINO tiny (Apache-2.0), prompt `insect.`, box threshold 0.35,
    text threshold 0.25;
  - the class comes from the observation's taxon;
  - the model is not added to the repository.
- Box review: the owner delegated it to the agent, which checked every overlay contact sheet.
  The policy keeps only images with exactly one correct box.
  - Excluded: **168** in total. 93 had several boxes, 18 had none, and 57 were single-box images
    flagged in review (nests, trees, screenshots, tiny or ambiguous insects, one box over several
    insects, wing only). The list is in `2026-10-22-inat-excluded.csv`.
  - Kept: **282** (velutina 66, crabro 102, other 114). Excluded files are moved to
    `train/excluded/` and never imported.
- Imported: inat-cc-by 229, inat-cc0 53. Photos of one observation share a group (AC10).

## Split and freeze

- Manifest has 2,099 rows: Sledevic 1,453, Roboflow 364, inat-cc-by 229, inat-cc0 53.
- `split --seed 0` was re-run after the frozen-set fix in `split_by_group`. The result is stable,
  and test equals test-v1.
- `freeze --id test-v1`: 288 images, SHA-256
  `6d4f5dc56b62eaab5ed15b91e25512a1f11f5ddcc4bd447366084952f0d654d9`.
  - By source: Sledevic 188 (one board), inat-cc-by 54, Roboflow 37, inat-cc0 9.

| Split | Images | apis_mellifera | other | vespa_crabro | vespa_velutina |
|---|---|---|---|---|---|
| train | 1,560 | 1,111 | 80 | 190 | 177 |
| validation | 251 | 152 | 16 | 46 | 37 |
| test (test-v1) | 288 | 188 | 18 | 32 | 50 |

Every class is present in every split.

## Known limits

- test-v1's bee frames all come from one landing board, so they say little about other hives.
- iNaturalist `cc-by` may cover CC BY 3.0 as well as 4.0 (ADR-0023). The per-photo attribution
  row is kept either way.
- The boxes were reviewed by an agent, not by a human. A human spot check before training is
  advised.
