# Local review — aristech (#174, pre-roll before the first motion frame)

- Date: 2026-11-06
- Scope: branch diff `origin/dev...fix/174-pre-roll-five-seconds` (ring = pre-roll + margin in
  `CampaignConfig`, adapter `ring_seconds` and pinned GOP, sidecar start, tests, capture-rig spec,
  sequence and state diagrams, bench-acceptance BA5 and follow-up)
- Checks run: adversarial review (findings, verify) · `mise x -- just check`
- Verdict: push gate open · Must 1 (fixed) · Should 7 (6 fixed, 1 deferred #178) · Nice 5 (4 fixed, 1 declined)

## Pre-push checks

| Step | Result |
|---|---|
| Tests | ✅ `just check`: 372 passed; coverage 98 % (floor 80) |
| Security | ✅ semgrep, osv, gitleaks clean |

## 🔴 Must Have

- `record_campaign.py`, spec, diagrams · the "≥ 5 s by design" claim ignored that a
  `CircularOutput2` clip starts on the first keyframe (Pi 5 default GOP 30 frames, ~1 s), so a 2 s
  margin left about 4.9 s minus the tick's work · **Fixed**: margin 3 s (ring 8 s),
  `H264Encoder(iperiod=fps)` pins a 1 s GOP (asserted in the adapter test), budget stated in the
  config comment and the docs.

## 🟡 Should Have

- BA5 still said the sidecar `start_utc` "is set from the pre-roll" · **Fixed**: computed as tick
  time − ring.
- The use-case test only re-checked the subtraction with exact 1 s ticks · **Fixed**: renamed the
  arithmetic test; new worst-case test with a 1.5 s tick, a 0.1 s latch and one GOP.
- The config comment named no budget · **Fixed**.
- A clip reopened within one ring of a close (including every 5-min cap) loses the old clip's
  last frames to the new one and its `end_utc` is off by up to ring − 1 s; the larger ring widens
  it · **Deferred**: pre-existing behaviour, #178.

## 🔵 Nice to Have

- "one-tick margin" naming · **Fixed**.
- Stale adapter test name `..._pre_roll_ring` · **Fixed**.
- Adapter default ring duplicates `CampaignConfig.ring` · **Fixed**: docstring points to it.
- No guard against a negative margin · **Declined**: the field is not exposed (YAGNI).

## ⚪ Disagree / intentional

- ADR-0017 still says "10 s ring": an accepted ADR is not edited, and 8 s fits that capacity.
- `reviews/feat-c1-recording-code.md` keeps the 5 s ring: dated record.

## Out of scope (pre-existing, follow-ups)

- Clip `start_utc` is computed, not the first frame's sensor timestamp (AV alignment, AC1): #179.
- `close()` drops the frames still in the ring at shutdown: #180.
- `timedatectl` (5 s timeout) runs inside a tick and can delay a clip open: #181.

## Verify round (on 9b4aae6)

All round-1 findings fixed except the deferred one (#178). New Should, fixed in the next commit:
the worst-case test now puts the motion 0.1 s before the earlier tick (latch worst case); the state
diagram and the config comment state the tick-work bound (< 0.9 s); this report is completed and the
follow-ups are filed. Nice: the spec paragraph re-wrapped. Gate line: open, 0 Must.
