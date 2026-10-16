# Spec — A0: acoustic feasibility gate

> **Status**: Proposed (needs brainstorm 2026-10-16) · **Milestone**: A0, after the 2027 capture
> season · **Related**: ADR-0016, ADR-0014, UC10

## Need

Decide on measured data whether sound can tell the presence of a hornet (wingbeat at the entrance)
or an attack (colony response) apart from the background of the hive and the wind, and so which
role audio plays — confirmer, wake-up, both, or none — before any audio code.

## Actors

- **Researcher** (primary).

## Reference signatures (captive lab, needs brainstorm Q9)

Before the field analysis, single captive *V. velutina* are recorded with no bees and no wind to
get a clean **reference wingbeat signature** (fundamental and harmonics). It tells the field
analysis which band to look for; it is never used as field evidence nor in the held-out split.

## Main scenario

1. From the synchronised recordings (spec `capture-rig`), the annotated video labels audio windows
   as *hornet present* / *absent* and *attack episode* / *calm*.
2. The researcher measures the SNR in the hornet wingbeat band against the hive + wind background,
   for both microphones.
3. A simple baseline (band energy threshold, or spectrogram + small classifier) is evaluated on a
   held-out split by day.
4. The result picks the role and is recorded in an ADR.

## Alternative scenarios

- **A1** Too few hornet windows → extend collection, gate stays open.
- **A2** Wingbeat inseparable but colony response separable → role limited to the attack alert.
- **A3** Neither separable → audio abandoned; the rig keeps video only.

## Acceptance criteria

- **AC1** The pass threshold (e.g. a minimum ROC-AUC on held-out days) is written before the
  analysis runs.
- **AC2** The labels come from the video annotation, not from listening.
- **AC3** The analysis is reproducible with one command on a versioned dataset.
- **AC4** Whatever the outcome, audio never forces an action in the decision path (ADR-0016).
