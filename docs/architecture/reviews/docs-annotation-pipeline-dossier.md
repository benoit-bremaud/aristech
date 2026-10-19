# Pre-push review — docs/annotation-pipeline-dossier (issue #95)

Scope: design dossier only (spec, 4 UML diagrams, ADR-0018 to ADR-0022, MCDA script, gate,
traceability). No source code.

| Check | Result |
|---|---|
| Documentation audit (consistency, links, Mermaid, MCDA vs script) | 0 Must, 6 Should — all fixed (see below), 5 Nice |
| MCDA totals and sensitivities vs `mcda/adr_0018_0022_annotation_pipeline.py` | match |
| Unit tests (`make test-unit`) | 174 passed, 2 skipped (unchanged code) |
| Secrets scan (gitleaks, branch commits) | no leaks |
| QA on running product | n/a (no runtime change) |

## Should — fixed

1. ADR-0019 claimed `data/registry/` already whitelisted → now "by PR 2", added to the staircase.
2. Spec A3: a duplicate image across groups now merges the groups (no frozen image in train).
3. Product use-case UC8 renamed to match the matrix.
4. ADR-0018: label `other` = `Species.UNKNOWN` stated.
5. ADR-0020: public group key stated as a weaker proxy for day-and-hive.
6. ADR-0022: Hailo column marked as estimate.

## Nice — kept as is

UC3 wording across diagrams, UC8 include-as-decomposition, ADR-0015 candidate list (closed by
ADR-0022), two unmarked facts (labelImg archive date, local GPU).
