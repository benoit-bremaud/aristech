# Spec — docs freshness and English (brick B6b)

> **Brick**: B6b · **Audit**: S2, English artefacts · **Issue**: #65 (S2 items) · **Out of scope**:
> S8 docstrings, #65 code nits, French code comments (B6c); Dependabot (B7)

## Need

A reader who opens the repository's Markdown documentation finds English text that describes the
system as built, with one source of truth per topic and no link to a missing file.

## Acceptance criteria

- **AC1** `docs/architecture.md` is a short English as-built overview: layers, the three ports
  (`VideoSource`, `HornetDetector`, `Notifier`), shipped adapters, `decide()` and abstention,
  `evaluation/`, `datasets/`, the real runtime flow, test levels, a condensed legal floor and open
  decisions linking ADR-0003/0004/0005/0009, and a pointer to `docs/architecture/` (S2).
- **AC2** No document presents `Target`, `NeutralizeTarget`, `AudioSource`, `DistanceSensor` or
  `Actuator` as part of the design (`docs/ROADMAP.md`, `docs/requirements.md`, `architecture.md`).
- **AC3** `docs/BOM.md` and `docs/DIY_INSTRUCTIONS.md` are deleted; `docs/INDEX.md` points to
  `docs/research/prototype-foundations.md` § B and § C (decision D1).
- **AC4** `README.md`, `docs/CONTRIBUTING.md`, `docs/INSTALL.md`, `docs/MAINTENANCE.md`,
  `models/README.md`, `tests/e2e/README.md` and `docs/requirements.md` are in English.
- **AC5** French left in `docs/research/` is verbatim citation only (law titles, legal terms,
  paper titles, proper names) (decision D2).
- **AC6** Every relative Markdown link in the touched files resolves.

## Decisions (owner-validated 2026-10-16)

- **D1** BOM/DIY: delete and point to `prototype-foundations.md` (485) vs rewrite in English (380)
  vs translate as is (180). Criteria: truth 40, single source 30, effort 15, reader value 15.
- **D2** research French: keep citations verbatim (470) vs translate them (290). Criteria: fidelity
  to sources 50, English rule 30, effort 20.

## Design impact

Documentation only; no code, UML or ADR change.
