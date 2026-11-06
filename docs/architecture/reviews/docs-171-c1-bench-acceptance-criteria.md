# Pre-push review — docs/171-c1-bench-acceptance-criteria

Pre-push review of the bench acceptance criteria for the C1 rig (issue #171), base `dev`
(`b6a19ed`), first head `7aec013`.

## Round 1 — adversarial review (findings)

Verdict: Must 8 · Should 9 · Nice 7 · Disagree 1. `just check` green.

| # | Level | Finding | Resolution |
|---|---|---|---|
| M1 | Must | BA16 asked for a muted second fault, impossible in one process (the run ends on the first) | Fixed: one `source_ended` push only; mute/count left to `test_health.py` |
| M2 | Must | BA14 delay measured on video time, which lags the wall clock on a replay | Fixed: measured from the wall-clock time of the "attack started" log line |
| M3 | Must | BA14 "one push per episode" ignored the end summary | Fixed: one alert and one summary |
| M4 | Must | `--push` needs the value `telegram` | Fixed in BA14–BA16 |
| M5 | Must | BA11 re-plugged the camera on a powered board, against its own safety note | Fixed: devices absent from power-on only; mid-run loss stays in unit tests |
| M6 | Must | BA20 read the instant under-voltage bit | Fixed: bit 16 (since boot), reboot before each run |
| M7 | Must | BA9 would delete the BA6–BA8 evidence | Fixed: run last, on a small loop filesystem, after copying the evidence |
| M8 | Must | BA8 13 GB/day band unreachable indoors | Fixed: audio and video rates scaled from ADR-0017 |
| S1 | Should | Auto-restart after a reboot does not exist | Fixed: BA7/BA10 need a follow-up service unit, listed |
| S2 | Should | Overruns are not logged; gaps not visible in FLAC | Fixed: frame-count check against the sidecar times |
| S3 | Should | Audio sidecars lack camera fields; `rtc` after a boot | Fixed: exact `to_dict` keys; `rtc` allowed on the first segment |
| S4 | Should | BA19 could pass outside the daylight window; no case in the BOM | Fixed: daylight window, bare board |
| S5 | Should | BA1 10-min count vs the 5-min clip cap | Fixed: per-clip count |
| S6 | Should | BA5 reading the sidecar is circular | Fixed: stopwatch in the scene, first motion frame by eye |
| S7 | Should | BA13 has no end; the camera is exclusive | Fixed: stop the recorder first, Ctrl-C after 10 min |
| S8 | Should | BA15 source, config and message count unclear | Fixed: full command, 21 min, four messages |
| S9 | Should | Review report missing | This file |
| N1–N5 | Nice | AC5 → AC2 and the sample clip; "each run" and repo root; `missing_inputs`; D1 and thin D2 margins cited; "(proposed)" in requirements | Fixed |
| N6 | Nice | Throttling starts near 80 °C, not 85 °C | Fixed: limit 75 °C, text corrected |
| N7 | Nice | An inline meter can break the 5 A negotiation | Fixed: `usb_max_current_enable` check in BA18 |
| D1 | Disagree | Keeping mid-run device loss in unit tests is right | Kept |

Out of scope (pre-existing): the once-per-second motion check may make the pre-roll shorter than
5 s (listed as a follow-up in the spec); `system_clock.py` reports `rtc` whenever `/dev/rtc0`
exists; `specs/README.md` and the UC7 matrix row still call built features "Proposed" / "planned".

## Round 2 — verification on `f936902`

All 24 round-1 findings verified fixed; gate open. New: Should 1 · Nice 4, all fixed in the next
commit.

| # | Level | Finding | Resolution |
|---|---|---|---|
| S10 | Should | USB webcam may not be `/dev/video0` on the Pi 5; not in the preconditions | Fixed: index from `v4l2-ctl --list-devices`; webcam added to the preconditions |
| N8 | Nice | No block size is set in the code | Fixed: ± 4 096 samples (≈ 85 ms) |
| N9 | Nice | BA6 and BA8 blocked with BA7 | Fixed: may run on a hand-started run of at least one day |
| N10 | Nice | Sample clip is not in the repo | Fixed: link to the attack-alert recipe |
| N11 | Nice | 75 °C heat limit is new | Put to the owner with the PR |

`just check` green on `f936902`.
