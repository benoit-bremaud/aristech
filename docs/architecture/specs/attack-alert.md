# Spec — attack alert: tell the beekeeper when an attack is under way

> **Status**: Accepted — episode rule and COUNT point built (issue #149); Telegram push, in-memory
> offline queue and fault path built (issue #152) · **Related**: ADR-0013, ADR-0014, ADR-0006,
> ADR-0031, ADR-0032, UC6 ·
> **UML**: [state](../diagrams/attack-alert/01-state.md),
> [sequence](../diagrams/attack-alert/02-sequence-live-alert.md)

## Need

The beekeeper must learn **while it happens** that a hive is under sustained hornet pressure, so
they can react (entrance reducer or muzzle, selective trap, visit) — without being flooded by a
notification per detection.

## Actors

- **Beekeeper** (primary) — receives the alert and responds to the attack (UC6).

## Main scenario

1. The system counts frames with a *V. velutina* detection that passes the COUNT operating point
   (ADR-0014, ADR-0031: lowest threshold with image precision ≥ 0.80; 0.15 for RF-DETR Small on
   test-v1).
2. When the count over a sliding window `W` reaches the pressure threshold `N`, an **attack episode**
   opens and **one** alert is pushed (start time, count; ADR-0032). The hive id and a
   representative frame come with the embedded deployment (M6).
3. While the episode lasts, no further alert is sent; the count keeps running in the log.
4. When the count stays below `N` for the cool-down `T`, the episode closes and is summarised in
   the log and pushed (duration, peak, total).
5. The beekeeper reads the alert and responds.

## Alternative scenarios

- **A1** System offline when an episode opens → the episode is logged locally and the alert is sent
  once back online, flagged as delayed (in-memory queue today, persistent with M6).
- **A2** Only *V. crabro* or bees → never counted, never alerted (non-target).
- **A3** Push channel fails → logged as a fault (ADR-0006 path); detection carries on.

## Acceptance criteria

- **AC1** A single alert per episode, whatever the number of detections in it.
- **AC2** Detections below the COUNT point, and non-target species, never contribute to `N`.
- **AC3** `N`, `W` and `T` are configuration values, set from field data at the conception gate,
  not hard-coded guesses.
- **AC4** The episode decision is a pure rule in the application layer, unit-tested with fake
  clocks and detection streams (no hardware).
- **AC5** No per-detection push exists in any configuration.
- **AC6** `COUNT ≤ ACT` holds for the model in use; the CLI also enforces detector floor ≤ COUNT.
- **AC7** A recorded video replays on its own time, so an episode measured on a clip matches the
  live scene.
- **AC8** A push channel failure never stops detection; it is logged as a fault, and the channel's
  secrets come from the environment only and never appear in the log (ADR-0032).

## Provisional values (ADR-0031)

`N = 3` hit frames, `W = 10 s`, `T = 60 s`, in the `alert` section of `config/config.yaml`. A
frame counts once, whatever its number of boxes. To set from the field set (M5).

## Verification (issue #149)

A 180-s sample clip built from test-v1 images at 1 fps (10 s hornets, 70 s empty, 10 s hornets,
70 s empty) run through the CLI with RF-DETR Small raised **two** alerts and two summaries, one per
episode; the same clip with 40-s gaps (shorter than `T`) raised one.

## Verification (issue #152)

An 80-s sample clip with one episode (the first 80 s of the #149 clip: 10 s hornets, 70 s empty), run with `--push telegram`
against a local Bot API stub (`ARISTECH_TELEGRAM_API_URL`), sent exactly one alert and one
summary, with no token in the log; the same run with the stub stopped logged `FAULT push channel` and finished normally.
