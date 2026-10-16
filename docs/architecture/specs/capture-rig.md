# Spec — C1: synchronised audio+video capture rig

> **Status**: Proposed (needs brainstorm 2026-10-16) · **Milestone**: C1, ready by July 2027 ·
> **Related**: ADR-0015, ADR-0016, ADR-0001, UC7

## Need

Record, unattended, a full hornet season of the hive entrance as **video plus two audio channels
on one clock**, because the own model (M5), the acoustic gate (A0) and the deterrence test (D0) all
need field data and no public synchronised dataset exists.

## Actors

- **Researcher** (primary) — installs the rig and collects recordings.
- **Beekeeper** — hosts the rig.

## Form (owner idea, needs brainstorm Q7)

A **watchtower on a stake** ("mirador"), about 0.5–1 m from the entrance and slightly above it
(estimate), looking down at the landing board so the background is hive and ground, not sky:

- flared, covered roof — rain, direct sun on the lens, heat;
- **slits**: one camera slit (window or opening with a drip visor) and one microphone slit (open,
  with wind foam or fur, never behind glass);
- body: compute board, storage and power (default target and parts fixed in this brick's ADR),
  insect-proof ventilation;
- **fixed, no rotation** for collection; extra slits designed in but blanked, to extend to
  neighbouring hives (one camera + mic each) once the single-hive unit is validated;
- the second (colony) microphone is cabled against or inside the hive;
- a rigid, vibration-free stake.
- form reference (owner idea, not frozen): a garden solar stake lamp — stake, small head with the
  slits, a cap as the roof;
- **power is remote** (owner decision 2026-10-16): the solar panel is far too large for the head, so it stands on its own
  well-exposed stake and feeds the battery and electronics by cable; mains power first, solar
  later. Panel and battery are **sized later**, from the prototype's measured consumption plus
  the battery recharge need — no sizing guess is fixed before that measurement. The cable run between the two stakes must stay out of the bees' flight path.

A rotating 360° turret was rejected (motor noise in the wingbeat band, moving background,
intermittent coverage of the entrance, moving parts outdoors); rotation belongs to v2 aiming.

## Main scenario

1. The rig (fixed camera over the flight volume, one microphone at
   the entrance with wind protection, one microphone inside or against the hive) is mounted.
2. It records in segments with a common timestamp for video and both audio channels, on motion or
   continuously in daylight (policy fixed at the gate).
3. Each segment's metadata (hive, time, settings, light, weather if known) is stored with it.
4. The researcher collects the segments (local disk swap or upload) for annotation.

## Alternative scenarios

- **A1** Disk nearly full → oldest non-flagged segments are dropped first and a fault is logged.
- **A2** A microphone fails → video keeps recording; the gap is logged.
- **A3** Human voices captured → trimmed before any sharing (privacy).

## Acceptance criteria

- **AC1** Audio–video drift ≤ one video frame over a segment (measured with a clap test).
- **AC2** The rig runs unattended for at least a week without intervention.
- **AC3** Every segment carries the metadata needed to split the test set by day and hive.
- **AC4** The recording code respects the dependency rule (camera / audio libraries in
  `infrastructure/`, behind an optional extra).
- **AC5** Mic models, sample rate (16–48 kHz) and enclosure are fixed in this brick's ADR.
- **AC6** No moving part inside the enclosure; the hornet hover volume (~10–50 cm in front of the
  landing board) is in frame with a hornet at least ~30 px long (estimate, checked at the gate).
