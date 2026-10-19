# Spec — C1: synchronised audio+video capture rig

> **Status**: Gate signed 2026-10-19; recording code in `src/aristech/` (extra `capture`) · **Milestone**: C1,
> ready by July 2027 · **Related**: ADR-0017 (hardware), ADR-0015, ADR-0016, ADR-0001, UC7 ·
> **UML**: [diagrams/capture-rig/](../diagrams/capture-rig/)

## Need

Record, unattended, a full hornet season (August–November) of one hive entrance as **video plus
two audio channels on one clock**, because the own model (M5), the acoustic gate (A0) and the
deterrence test (D0) all need field data and no public synchronised dataset exists. The rig is
**neutral**: it records, it never detects nor acts.

## Actors

| Actor | Kind | Goal |
|---|---|---|
| **Researcher** | primary, human | Install the rig, start/stop a campaign, collect segments for annotation (UC7). |
| **Beekeeper** | secondary, human | Host the rig at the hive; never has to touch it. |
| **Bees, hornets, weather** | environment | Source of motion and sound; not actors in UML terms. |

The motion trigger, the daylight clock and the disk watchdog are **system events inside UC7**,
not use cases.

## Form (owner, needs brainstorm Q7)

A **watchtower on a stake** ("mirador"), about 0.5–1 m from the entrance and slightly above it,
looking down at the landing board so the background is hive and ground, not sky:

- flared, covered roof (form reference: a garden solar stake lamp — stake, small head, cap roof);
- **slits**: one camera slit (window with a drip visor) and one microphone slit (open, wind foam
  or fur, never behind glass); extra slits designed in but blanked, for neighbouring hives later;
- body: compute board, storage, power entry, insect-proof ventilation (mesh ≤ 2 mm);
- **fixed, no moving part**; a rigid, vibration-free stake;
- the second (colony) microphone is cabled against or inside the hive (cable ≤ 1.5 m);
- **power is remote**: mains first; for the remote site a solar panel on its own stake, sized from
  the prototype's **measured** consumption (no guess fixed before that); the cable run between the
  stakes stays out of the bees' flight path.

A rotating 360° turret was rejected (motor noise in the wingbeat band, moving background,
intermittent coverage, moving parts outdoors).

## Sites and recording policy (needs brainstorm Q8, Q10)

- **Unit 1 at home** — mains power, Wi-Fi upload, daily supervision. **Unit 2 later at the remote
  apiary** — solar stake, local storage, visits every 2–3 weeks.
- **Audio**: both channels continuous during the daylight window (sunrise − 30 min to sunset +
  30 min, computed from the site's latitude/longitude, no network needed), FLAC, 48 kHz, 24-bit,
  split into 10-minute segments.
- **Video**: 1920×1080 at 30 fps kept in a **RAM ring buffer of 10 s**; on motion in the region of
  interest, the clip is saved from **5 s before** the first motion frame to **5 s after** the last
  one (clips merge when events overlap; a clip is capped at 5 min). Values are defaults, set in a
  config file, revisited after the first week of footage.
- **Budget**: not set; ADR-0017 prices a BOM the owner validates before ordering.

## Data per segment

Every audio segment and video clip is a file plus a JSON sidecar: `rig_id`, `hive_id`,
`site`, start/end timestamps (UTC, ns, from the shared monotonic clock mapped to UTC once per
segment), sample rate / resolution / fps, camera exposure and gain, clock source (NTP / RTC),
light level (camera lux estimate), `trigger` (`continuous` / `motion`), `flagged` (kept from
rotation), software version (git SHA). Weather is added offline from a public source by date.

## Main scenario — record a campaign (UC7)

1. The Researcher mounts the rig, sets `rig_id`, `hive_id` and the site coordinates, and starts a
   campaign.
2. The rig checks its clock (NTP, else RTC), both microphones and the camera, then enters
   *Recording*.
3. In the daylight window, audio is written continuously; video frames fill the ring buffer.
4. On motion in the region of interest, the buffered pre-roll plus the live frames until the
   post-roll ends are saved as one clip, timestamped on the same clock as audio.
5. At the end of the daylight window the rig enters *Idle* (no recording) until the next window.
6. The Researcher collects segments: Wi-Fi sync (home) or SSD swap (remote site).

## Alternative scenarios

- **A1 Disk nearly full** (< 10 % free) → oldest non-flagged segments are deleted first, a fault
  line is logged; below 2 % free, recording stops and the rig enters *Fault*.
- **A2 A microphone fails** (no samples or flat signal for 10 s) → video and the other channel go
  on; the gap is logged and written in the sidecars.
- **A3 Camera fails** (at start or mid-run) → audio goes on; fault logged; the rig retries the
  camera at every self-check tick (1 s).
- **A4 Clock unsynchronised** (no NTP, RTC not set) → recording goes on, sidecars carry
  `clock_source: unsynced`; the Researcher fixes it at the next visit.
- **A5 Power loss** → on restart the rig resumes the campaign by itself; at most the open segment
  is lost (segments are closed every 10 min).
- **A6 Human voices captured** → trimmed before any sharing (privacy); never published raw.

## Acceptance criteria

| AC | Criterion | How it is verified |
|---|---|---|
| **AC1** | Audio–video offset ≤ 33 ms (one frame at 30 fps) at the start and end of a 10-min segment | Clap test: clap in front of the rig, compare the clap frame time with the audio onset in both channels |
| **AC2** | Runs unattended ≥ 7 days with no manual action and no lost daylight hour | Field log of a 7-day run at home: segment count vs expected daylight minutes |
| **AC3** | Every segment has a complete sidecar allowing a split by day and hive | Unit test on the sidecar writer; script check over the 7-day run |
| **AC4** | Dependency rule kept: camera / audio libraries only in `infrastructure/`, behind the `capture` extra; domain and application import none | `import-linter`-style unit test + review |
| **AC5** | Mic models, sample rate and enclosure fixed in ADR-0017 | ADR accepted |
| **AC6** | No moving part; a 30 mm object 10–50 cm in front of the landing board spans ≥ 30 px | Ruler test with the mounted camera at install |
| **AC7** | Motion clip contains ≥ 5 s of pre-roll before the first motion frame | Unit test with fake camera + fake clock; field check on 10 clips |
| **AC8** | A1, A2, A3, A5 behave as described (fault logged, other streams continue, auto-resume) | Unit tests with hand-written fakes; one pulled-plug test in the field |
| **AC9** | Power draw measured over 24 h (mean and peak) and recorded, as input to the solar sizing | USB-C power meter log committed in `docs/research/` |

## Out of scope

Detection, deterrence, annotation tooling (own brick), solar sizing (after AC9), unit 2.
