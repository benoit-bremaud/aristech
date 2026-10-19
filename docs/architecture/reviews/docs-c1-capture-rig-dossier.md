# Pre-push review — `docs/c1-capture-rig-dossier`

> **Scope**: docs-only — C1 spec refined, `capture-rig` UML (use-case, sequence, component,
> state), ADR-0017 with its MCDA script, conception gate (signed 2026-10-19), traceability and
> ADR index. No product code.

## Checks

- MCDA totals and every sensitivity case recomputed by `docs/decisions/mcda/adr_0017_capture_rig_hardware.py`;
  weights sum to 100 (asserted); flips (camera → HQ, storage → USB SSD) stated in the ADR.
- markdownlint clean on every changed file; all relative links resolve.
- `ruff check` + `ruff format --check` clean on the MCDA script.
- Secrets scan (gitleaks on `main..HEAD`): no leaks.

## 🔴 Must Have

None.

## 🟡 Should Have

- Fixed: MCDA script failed `ruff check` / `ruff format` (CI lint) → rewritten with typed helpers.

## 🔵 Nice to Have

- Deferred: BOM prices are estimates; to be confirmed against a supplier before ordering.

## ⚪ Disagree / Intentional

- Ports `CameraRecorder`, `AudioRecorder`, `SegmentStore`, `Clock` are designed (not coded) here;
  each has a real adapter and a test fake, so ADR-0010's force holds.
