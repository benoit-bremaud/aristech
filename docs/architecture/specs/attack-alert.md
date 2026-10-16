# Spec — attack alert: tell the beekeeper when an attack is under way

> **Status**: Proposed (needs brainstorm 2026-10-16) · **Milestone**: after M6 (push channel) and
> M4 two operating points · **Related**: ADR-0013, ADR-0014, ADR-0006, UC6

## Need

The beekeeper must learn **while it happens** that a hive is under sustained hornet pressure, so
they can react (entrance reducer or muzzle, selective trap, visit) — without being flooded by a
notification per detection.

## Actors

- **Beekeeper** (primary) — receives the alert and responds to the attack (UC6).

## Main scenario

1. The system counts *V. velutina* detections that pass the COUNT operating point (ADR-0014).
2. When the count over a sliding window `W` reaches the pressure threshold `N`, an **attack episode**
   opens and **one** alert is sent (hive, start time, count, a representative frame).
3. While the episode lasts, no further alert is sent; the count keeps running in the log.
4. When the count stays below `N` for the cool-down `T`, the episode closes and is summarised in
   the log (duration, peak, total).
5. The beekeeper reads the alert and responds.

## Alternative scenarios

- **A1** System offline when an episode opens → the episode is logged locally and the alert is sent
  once back online, flagged as delayed.
- **A2** Only *V. crabro* or bees → never counted, never alerted (non-target).
- **A3** Push channel fails → logged as a fault (ADR-0006 path).

## Acceptance criteria

- **AC1** A single alert per episode, whatever the number of detections in it.
- **AC2** Detections below the COUNT point, and non-target species, never contribute to `N`.
- **AC3** `N`, `W` and `T` are configuration values, set from field data at the conception gate,
  not hard-coded guesses.
- **AC4** The episode decision is a pure rule in the application layer, unit-tested with fake
  clocks and detection streams (no hardware).
- **AC5** No per-detection push exists in any configuration.
