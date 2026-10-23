# ADR-0023: Fetch iNaturalist photos with a stdlib script and per-photo attribution

- Status: Accepted (owner, 2026-10-22)
- Date: 2026-10-22 (issue #95, PR 3; step 2 of ADR-0021)

## Context

ADR-0021 step 2 adds iNaturalist research-grade photos licensed CC BY or CC0. The licence and
the author are set **per photo**, and CC BY requires attribution of each work. The signed gate
(`gates/annotation-pipeline.md`) does not say how the photos are fetched. The iNaturalist API v1
(`/v1/observations`) filters on `quality_grade=research`, `photo_license` and `taxon_id`, and returns
each photo's licence code and attribution string (checked 2026-10-22, public, no login).
Photos of one observation show the same animal: they must share a group (ADR-0020).

## Options (MCDA)

Script: [`mcda/adr_0023_inaturalist_fetch.py`](mcda/adr_0023_inaturalist_fetch.py). Scores 0–5,
weights /100, totals /500; scores are estimates.

| Option | Traceability 35 | Licence safety 25 | Dependencies / KISS 20 | Effort 20 | Total |
|---|---|---|---|---|---|
| A. Stdlib script on API v1, per-photo attribution file | 5 | 5 | 4 | 3 | **440** |
| B. Manual export from the iNaturalist website | 2 | 4 | 5 | 3 | 330 |
| C. `pyinaturalist` library | 5 | 5 | 2 | 4 | 420 |

Sensitivity (renormalised to 100): dependencies 30 → A 430, C 390; effort 30 → A 420, C 410;
traceability 25 + effort 30 → A 420, C 410. A stays first; A vs C is close on effort only, A vs B
is per-photo attribution, which B loses.

## Decision

- `scripts/inat_fetch.py` (stdlib `urllib`, `json`, `csv`) fetches research-grade observations of a
  taxon, keeps only photos with licence `cc-by` or `cc0`, caps the count per taxon, and writes
  `data/external/inat-<licence>/train/images/<observation_id>_<photo_id>.jpg` (git-ignored).
- One licence-register source per licence: `inat-cc-by` (CC-BY-4.0) and `inat-cc0` (CC0-1.0).
  The API's `license_code` carries no version; iNaturalist's licence chooser offers the 4.0
  texts, so the register records CC-BY-4.0 (estimate for very old uploads, see Consequences).
- Per-photo attribution goes to the committed text file `data/registry/inat-attribution.csv`
  (photo id, observation id, taxon, licence, attribution, URL). No pixels.
- New group rule `observation`: the group key drops the trailing `_<photo_id>`, so every photo
  of an observation shares one group.
- Boxes come from X-AnyLabeling pre-annotation corrected by the owner (ADR-0018); labels land in
  `train/labels/` next to the images, then the normal `dataset.py import` runs.

## Consequences

- iNaturalist is called politely (one request per page, a pause between requests, a user agent
  naming the project). The script is not run in CI; its pure parts (filtering, naming, rows) are
  unit-tested.
- Photos with an NC, ND or unknown licence never reach the disk.
- Risk: a photo uploaded before iNaturalist moved to the 4.0 texts may be CC BY 3.0. Both
  versions allow our use with attribution; the attribution row keeps the photo URL, so the
  exact version stays checkable.
