# Local review — aristech (#179, clip start from the first frame's sensor time)

- Date: 2026-11-06
- Scope: branch diff `origin/dev...fix/179-clip-start-sensor-timestamp` (`CameraRecorder.start_clip`
  returns the first frame's UTC time, Picamera2 first-frame tap, `RecordCampaign` clip start,
  tests, sequence diagram)
- Checks run: adversarial review (findings, verify) · `mise x -- just check`
- Verdict: push gate open after round 3; round 4 after the hosted review · Must 4 (fixed) · Should 4 (fixed) · Nice 6 (fixed)

## Pre-push checks

| Step | Result |
|---|---|
| Tests | ✅ `just check` green; coverage above the 80 % floor |
| Security | ✅ semgrep, osv, gitleaks clean |

## 🔴 Must Have

- `picamera2_recorder.py` · the 0.5 s wait was shorter than one GOP: after `open_output` the ring
  drops frames until a keyframe is one ring old (0 to 1 s, about half the clips above 0.5 s), so
  the worst clips kept the error · **Fixed**: wait up to 1.2 s; the pre-roll is fixed before the
  wait, so it costs only the opening tick's length.
- `record_campaign.py` · the previous clip's end was dated at the new first frame, but the old
  output closes at the ring front and the frames up to the new first keyframe are in neither
  file · **Fixed**: the old end stays at the ring front (`now − ring`); the diagram and docstring
  state the gap of under one GOP.
- The "one clock" rule was stated differently in the port, the use case and the sequence
  diagram · **Fixed**: one sentence in all three (device time where it knows better, else the
  `Clock`; all UTC wall time).

- Verify round: the plausibility check's lower bound `now − ring` rejected correct times, since
  the ring ages frames against the newest one, which arrives a pipeline latency after its sensor
  time · **Fixed**: one GOP of slack below; a test keeps a time 50 ms before the ring front.

## 🟡 Should Have

- Adapter tests passed with a tap that never forwarded frames · **Fixed**: the fake ring calls
  `start` / `_add_stream` / `stop`, delivers the keyframe on a timer, and the test asserts the
  frames reach the wrapped output; a test delivers it after 0.9 s.
- No check on the adapter's time, which depends on picamera2 internals · **Fixed**: a time
  outside `[now − ring, now]` is logged and replaced by the fallback (widened by one GOP in the
  verify round).
- This report was missing · **Fixed**.
- Verify round: two test names still said the old clip ends where the next starts · **Fixed**:
  renamed to the ring-front rule.

## 🔵 Nice to Have

- The tap now forwards the frame in a `finally`, so the timing code never blocks the write ·
  **Fixed**.
- Fallback wording in two use-case tests · **Fixed**.
- Verify round: the first-frame event is set after the frame is forwarded; the docstring wrap
  is fixed; the fake ring cancels its keyframe timer · **Fixed**.
- CLOCK_BOOTTIME vs CLOCK_MONOTONIC note (equal on a Pi that never suspends) · **Fixed**.

## ⚪ Disagree / intentional

- Reading the private `CircularOutput2._time_offset` is the owner-approved MCDA option A; a
  missing attribute or an implausible time falls back.

## Out of scope (pre-existing)

- A close timer firing while a clip reopens can make `close_output` / `open_output` raise
  (from #178, #190) and back-to-back clips lose up to one GOP of frames (#191).
- Spec and ADR-0017 still say "shared monotonic clock" (#186; the ADR is superseded, not edited).

## Hosted review (after push)

- `record_campaign.py` · a new start inside the one-GOP slack below the ring front came before
  the old clip's end (`now − ring`), so the sidecars overlapped · **Fixed**: the old end is
  capped at the new start; test added.
- Round 4 (verify of that fix): push gate open · Should 1 (docstring and diagram arrow gave the
  old end without the cap) and Nice 2 (rewraps) · **Fixed**.
