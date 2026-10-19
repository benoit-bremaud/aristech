# Architecture Decision Records

`ADR-NNNN-<slug>.md`, numbered in order, never renumbered. Each ADR records the context, the
options with their MCDA scores, the decision and its consequences. An accepted ADR is never
edited; a new ADR supersedes it.

Status values: `Proposed`, `Accepted`, `Superseded by ADR-NNNN`.

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-0001](ADR-0001-clean-architecture-and-optional-extras.md) | Clean Architecture with ports and optional heavy extras | Accepted |
| [ADR-0002](ADR-0002-wrap-vespai-baseline-first.md) | Wrap the VespAI YOLOv5 model as the first detector | Superseded by ADR-0015 |
| [ADR-0003](ADR-0003-legal-floor-abstain-by-default.md) | Legal floor: never act on a bee, abstain by default | Accepted |
| [ADR-0004](ADR-0004-operating-point-zero-bee-threshold.md) | Operating point: lowest threshold with zero bees as target | Superseded by ADR-0014 |
| [ADR-0005](ADR-0005-non-lethal-deterrent-decoupled.md) | Non-lethal water-jet deterrent, decoupled from detection and gated by D0 | Accepted |
| [ADR-0006](ADR-0006-observability-over-alerts.md) | Observability model instead of per-detection alerts | Superseded by ADR-0013 |
| [ADR-0007](ADR-0007-security-and-quality-ci-baseline.md) | Security CI baseline and local SonarQube | Accepted |
| [ADR-0008](ADR-0008-adopt-vsea-cubbies-method.md) | Adopt the V-SEA / cubbies working method | Accepted |
| [ADR-0009](ADR-0009-detector-floor-and-abstention-reporting.md) | Separate detector floor from operating threshold; report abstentions | Accepted |
| [ADR-0010](ADR-0010-remove-speculative-ports-and-legacy-training.md) | Remove speculative ports, unused extras and the legacy Keras training package | Accepted |
| [ADR-0011](ADR-0011-drop-sphinx-stub-and-lint-parity.md) | Drop the Sphinx stub and align `make lint` with CI | Accepted |
| [ADR-0012](ADR-0012-vision-extra-security-floors.md) | Security floors for the `vision` extra (Dependabot relock) | Accepted |
| [ADR-0013](ADR-0013-monitoring-with-aggregated-attack-alert.md) | Monitoring with an aggregated attack alert | Accepted |
| [ADR-0014](ADR-0014-two-operating-points-act-and-count.md) | Two operating points: zero-bee to act, high precision to count | Accepted |
| [ADR-0015](ADR-0015-own-vision-model-on-permissive-base.md) | Own vision model on a permissively licensed pre-trained base | Accepted |
| [ADR-0016](ADR-0016-acoustic-axis-collect-then-gate.md) | Acoustic axis: collect synchronised audio first, decide its role on data | Accepted |
| [ADR-0017](ADR-0017-capture-rig-hardware.md) | Capture-rig hardware: Pi 5, Camera Module 3, 2 × ICS-43434, NVMe, PVC watchtower | Accepted |
| [ADR-0018](ADR-0018-annotation-tool-and-label-format.md) | X-AnyLabeling as annotation tool, YOLO txt as canonical label format | Proposed |
| [ADR-0019](ADR-0019-dataset-storage-and-licence-register.md) | Committed manifest and licence register; pixels stay git-ignored | Proposed |
| [ADR-0020](ADR-0020-frozen-test-set-policy.md) | Frozen test set — group-keyed, hash-listed, versioned and append-only | Proposed |
| [ADR-0021](ADR-0021-public-datasets-for-the-pre-field-model.md) | Public datasets for the pre-field model | Proposed |
| [ADR-0022](ADR-0022-base-detector-rf-detr.md) | RF-DETR (Apache-2.0 sizes) as the base detector of the own model | Proposed |
