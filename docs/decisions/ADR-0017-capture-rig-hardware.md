# ADR-0017: Capture-rig hardware — compute board, camera, microphones, storage, enclosure

- Status: Proposed (owner validation of weights and BOM pending)
- Date: 2026-10-19 (brick C1)

## Context

Spec [capture-rig](../architecture/specs/capture-rig.md) needs a fixed rig recording 1080p30
motion clips from a 10 s RAM ring buffer and two audio channels (entrance + colony) on one clock,
unattended for weeks, mains first and solar later. The rig is neutral (no inference), but its
board should be reusable for the embedded detector (M6), for which `requirements.md` already
points to a Raspberry Pi 5 + AI HAT+. Data rate (estimate): video ~8 Mbit/s × ~2 h motion/day ≈
7 GB, audio 2 ch × 48 kHz × 24 bit FLAC ≈ 6 GB per 12 h → **~13 GB/day**, ~90 GB/week.

Totals and sensitivity are computed by
[`mcda/adr_0017_capture_rig_hardware.py`](mcda/adr_0017_capture_rig_hardware.py). Scores 0–5,
weights /100, totals /500. Scores are estimates from datasheets and community reports, not
measurements.

## 1. Compute board

Criteria: capture capability (encode 1080p30, 10 s ring in RAM, 2-ch I²S) 30 · power 20 · cost 20 ·
reuse for M6 15 · supply / ecosystem 15.

| Option | Capture | Power | Cost | M6 | Supply | Total |
|---|---|---|---|---|---|---|
| **A. Raspberry Pi 5 8 GB** | 5 — strong CPU (no HW H.264 encoder, but software 1080p30 fits), RAM ample | 2 — ~4–6 W recording | 3 | 5 — AI HAT+ path | 5 | **400** |
| B. Raspberry Pi 4 4 GB | 4 — HW encoder, enough RAM | 3 | 4 | 2 — no AI HAT+ | 4 | 350 |
| C. Raspberry Pi Zero 2 W | 2 — 512 MB, ring buffer tight | 5 | 5 | 0 | 3 | 305 |
| D. Jetson Orin Nano | 4 — camera / I²S integration fiddly | 1 | 1 | 4 | 3 | 265 |

Sensitivity: power 35 (capture 30, cost 15, M6 10, supply 10) → A 365, B 345, C 340; cost 30
(capture 20, power 20, M6 15, supply 15) → A 380, B 350; M6 0 (capture 30, power 20, cost 20,
supply 30) → A 400, B 380. **A stays first** in every case.

## 2. Camera + lens

Criteria: pixels on a hornet at 0.5–1 m 30 · motion blur 20 · cost 15 · fits the small head 20 ·
low light / dynamic range 15.

| Option | Px | Blur | Cost | Fits | Low light | Total |
|---|---|---|---|---|---|---|
| **A. Camera Module 3 (IMX708, 66° H, autofocus)** | 4 — ~60 px / 30 mm at 0.75 m | 3 | 5 | 5 | 3 | **400** |
| B. Camera Module 3 Wide (102° H) | 2 — ~31 px, marginal for AC6 | 3 | 5 | 5 | 3 | 340 |
| C. HQ Camera + 6 mm CS lens | 5 | 3 | 2 | 2 — bulky | 5 | 355 |
| D. Global Shutter Camera + 6 mm lens | 3 — 1.6 MP | 5 | 2 | 2 | 3 | 305 |

Sensitivity: blur 35 (px 20, cost 15, fits 15, low light 15) → A 380, others 340; px 40 (blur 15,
cost 10, fits 15, low light 20) → **C 395 > A 390 (flips)**; low light 30 (px 30, blur 20, cost
15, fits 5) → **C 400 > A 370 (flips)**. A wins as long as the small head matters; if the owner
values image quality over head size, C wins. Owner to arbitrate through the weights.

## 3. Microphones

Criteria: fidelity in the 100–1000 Hz wingbeat band 30 · both channels on one clock 30 · cable
run to the hive 15 · cost 10 · simplicity 15.

| Option | Band | One clock | Cable | Cost | Simple | Total |
|---|---|---|---|---|---|---|
| **A. 2 × ICS-43434 on one I²S bus (L/R)** | 4 — flat 60 Hz–20 kHz, 24-bit | 5 — one stereo stream | 3 — I²S over ≤ 1.5 m shielded cable, to verify | 5 | 4 | **425** |
| B. 2 × SPH0645 on one I²S bus | 3 — known DC offset / low-end roll-off | 5 | 3 | 5 | 4 | 395 |
| C. USB audio interface + 2 analog mics | 4 | 2 — separate clock from the camera path | 5 | 3 | 3 | 330 |

Sensitivity: cable 30 (band 30, clock 15, cost 10, simple 15) → A 395, C 375, B 365; band 40
(clock 20, cable 15, cost 10, simple 15) → A 415. **A stays first.** Risk: the colony mic's I²S
run; fallback = shorten to 1 m or use a small differential I²S line driver (adds ~10 €).

## 4. Storage

Criteria: write endurance 30 · capacity 25 · power 15 · cost 15 · simplicity 15.

| Option | Endurance | Capacity | Power | Cost | Simple | Total |
|---|---|---|---|---|---|---|
| A. High-endurance microSD 256 GB only | 2 | 1 — ~2.5 weeks | 5 | 5 | 5 | 310 |
| B. USB 3 SSD 1 TB | 4 | 5 | 3 | 3 | 4 | 395 |
| **C. M.2 HAT+ + NVMe SSD 1 TB** | 5 | 5 | 3 | 3 | 3 | **410** |

Sensitivity: simplicity 25 (endurance 20, cap 25, power 15, cost 15) → **B 395 > C 390 (flips)**;
endurance 40 (cap 25, power 15, cost 10, simple 10) → C 430, B 400. Close call; C keeps the
storage inside the head with no cable to work loose. OS stays on a high-endurance microSD.

## 5. Enclosure (no matrix: one option fits the owner's form)

Garden-solar-lamp form: a ~110 mm PVC pipe head on a galvanised stake, a flared cap as roof,
acrylic camera window with drip visor, open mic slit with fur windscreen, M12 cable glands,
stainless insect mesh vents, the Pi on a printed internal frame. Moving parts: none.

## Decision (proposed)

A Pi 5 8 GB · Camera Module 3 · 2 × ICS-43434 · NVMe 1 TB on M.2 HAT+ · PVC watchtower.
Software: Picamera2 (`CircularOutput`, software H.264), ALSA I²S overlay + `sounddevice` →
FLAC, all in the `capture` optional extra.

## Bill of materials (estimates, EUR incl. VAT, October 2026; prices to confirm at order)

| # | Part | Qty | Unit € | Total € |
|---|---|---|---|---|
| 1 | Raspberry Pi 5 8 GB | 1 | 95 | 95 |
| 2 | Official 27 W USB-C power supply | 1 | 13 | 13 |
| 3 | Active cooler | 1 | 6 | 6 |
| 4 | RTC backup battery (Pi 5 connector) | 1 | 6 | 6 |
| 5 | Camera Module 3 (standard) | 1 | 27 | 27 |
| 6 | Camera cable 22→15 pin, 200 mm | 1 | 3 | 3 |
| 7 | ICS-43434 I²S breakout | 2 | 12 | 24 |
| 8 | Shielded 6-core cable 2 m + JST connectors | 1 | 10 | 10 |
| 9 | Fur / foam windscreens | 2 | 4 | 8 |
| 10 | M.2 HAT+ | 1 | 13 | 13 |
| 11 | NVMe SSD 1 TB (2230/2242) | 1 | 70 | 70 |
| 12 | High-endurance microSD 64 GB (OS) | 1 | 15 | 15 |
| 13 | Enclosure: PVC pipe + cap, stake, acrylic window, glands, mesh, fixings | 1 | 40 | 40 |
| 14 | USB-C power meter (AC9) | 1 | 15 | 15 |
| | **Total unit 1 (mains)** | | | **≈ 345** |

Excluded: outdoor mains extension (owner's), solar panel and battery (sized after AC9), unit 2.

## Consequences

- New optional extra `capture` (picamera2, sounddevice, soundfile); never in core dependencies.
- New ports `CameraRecorder`, `AudioRecorder`, `SegmentStore`, `Clock`, each with a real adapter
  and a test fake (ADR-0010 force).
- AC1 (one-frame sync) depends on one monotonic clock for both streams; checked by clap test.
- If the owner shifts weights so that a matrix flips (camera → HQ, storage → USB SSD), the BOM
  changes accordingly (HQ + lens ≈ +60 €; USB SSD ≈ same price).
