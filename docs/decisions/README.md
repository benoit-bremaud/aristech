# Architecture Decision Records

`ADR-NNNN-<slug>.md`, numbered in order, never renumbered. Each ADR records the context, the
options with their MCDA scores, the decision and its consequences. An accepted ADR is never
edited; a new ADR supersedes it.

Status values: `Proposed`, `Accepted`, `Superseded by ADR-NNNN`.

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-0001](ADR-0001-clean-architecture-and-optional-extras.md) | Clean Architecture with ports and optional heavy extras | Accepted |
| [ADR-0002](ADR-0002-wrap-vespai-baseline-first.md) | Wrap the VespAI YOLOv5 model as the first detector | Accepted |
| [ADR-0003](ADR-0003-legal-floor-abstain-by-default.md) | Legal floor: never act on a bee, abstain by default | Accepted |
| [ADR-0004](ADR-0004-operating-point-zero-bee-threshold.md) | Operating point: lowest threshold with zero bees as target | Accepted |
| [ADR-0005](ADR-0005-non-lethal-deterrent-decoupled.md) | Non-lethal water-jet deterrent, decoupled from detection and gated by D0 | Accepted |
| [ADR-0006](ADR-0006-observability-over-alerts.md) | Observability model instead of per-detection alerts | Accepted |
| [ADR-0007](ADR-0007-security-and-quality-ci-baseline.md) | Security CI baseline and local SonarQube | Accepted |
| [ADR-0008](ADR-0008-adopt-vsea-cubbies-method.md) | Adopt the V-SEA / cubbies working method | Accepted |
| [ADR-0009](ADR-0009-detector-floor-and-abstention-reporting.md) | Separate detector floor from operating threshold; report abstentions | Accepted |
| [ADR-0010](ADR-0010-remove-speculative-ports-and-legacy-training.md) | Remove speculative ports, unused extras and the legacy Keras training package | Accepted |
