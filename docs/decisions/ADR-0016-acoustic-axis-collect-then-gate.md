# ADR-0016: Acoustic axis — collect synchronised audio first, decide its role on data

- Status: Accepted
- Date: 2026-10-16 (needs brainstorm, Q5)

## Context

The owner wants to combine image and sound. Two acoustic signals are plausible (literature, not yet
measured here): the *V. velutina* wingbeat, lower in frequency than the honeybee's, while it hovers
at the landing board; and the colony's collective response to an attack (shimmering, hissing). The
unknown is the signal-to-noise ratio at a real hive, among thousands of bees and the wind. No public
synchronised audio+video dataset of hornet attacks exists. ADR-0010 deleted the speculative
`AudioSource` / `SoundClassifier` ports for lack of a consumer.

## Options (MCDA)

Criteria and weights: risk reduction / information 30, cost now 20, value potential 25,
YAGNI / architecture 25. Scores 0–5.

| Option | C1 | C2 | C3 | C4 | Total /500 |
|---|---|---|---|---|---|
| A. Design the audio confirmer + fusion now, build after M5 | 3 | 3 | 5 | 3 | 350 |
| B. Record synchronised audio+video from the first capture campaign; feasibility gate A0; role and port decided on data | 5 | 4 | 4 | 5 | **455** |
| C. Audio as a low-power wake-up trigger | 2 | 3 | 3 | 3 | 270 |
| D. No audio | 0 | 5 | 0 | 5 | 225 |

Sensitivity (script-checked): with cost at 30 (YAGNI 15), B 445, A 350; with value potential at 50
(information 20, cost 15, YAGNI 15), B 435, A 400. B stays first. **Chosen: B** (owner, 2026-10-16).

## Decision

- The capture rig (spec `capture-rig`) records **two microphones** — one at the entrance (wingbeat),
  one inside or against the hive (colony response) — **on the same clock as the camera**. The
  annotated video then labels the audio for free.
- **Gate A0** (spec `acoustic-feasibility`): on recorded hours with and without hornets, measure the
  SNR in the hornet band and test whether a simple classifier separates presence from absence. The
  outcome picks the role: confirmer, wake-up, both, or abandon.
- **No audio code before a positive A0.** After it: an `AudioDetector` port (justified by a real
  second sensor and adapter), an `AcousticEvidence` domain type, and fusion as a pure decision rule.
- **Standing safety rule**: in the action path, audio may only **reinforce abstention** (AND
  fusion); it can never force an action the vision ACT point (ADR-0014) did not allow. In the
  counting / alert path, a combined score or OR fusion is allowed (decided after A0).

## Consequences

- New use case UC10 *Assess the acoustic signal*; the hardware BOM gains two I²S MEMS microphones
  with wind protection (estimate; fixed in the capture-rig brick).
- Recordings are personal-data-free (no human voices expected at a hive entrance); if voices are
  captured, they are trimmed before any sharing (privacy).
- The acoustic axis leaves "deferred" in `requirements.md` for data collection only.
