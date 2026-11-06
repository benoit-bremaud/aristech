# Local review — aristech (#178, end of a clip reopened within one ring)

- Date: 2026-11-06
- Scope: branch diff `origin/dev...fix/178-clip-tail-ring` (deferred video sidecar in
  `RecordCampaign`, adapter docstring, tests, capture-rig spec, sequence and state diagrams)
- Checks run: adversarial review (findings, verify) · `mise x -- just check`
- Verdict: push gate open · Must 1 (fixed) · Should 2 (fixed) · Nice 8 (6 fixed, 2 declined)

## Pre-push checks

| Step | Result |
|---|---|
| Tests | ✅ `just check`: 379 passed; coverage 97 % (floor 80) |
| Security | ✅ semgrep, osv, gitleaks clean |

## 🔴 Must Have

- `record_campaign.py` · a FAULT during the ring wrote the closing sidecar at once with the stop
  tick, so a clip reopened on the next tick overlapped it again (the #178 case); a failed write
  lost the sidecar · **Fixed**: the sidecar is written only when the ring elapses (first step of a
  tick), when the next clip opens, or on `close()`; it is kept on a write error and retried.

## 🟡 Should Have

- `close()` dated the end at the stop tick, but releasing the camera closes the pending output at
  once · **Fixed**: `close()` ends it one ring before the release; diagram note points to #180.
- The old sidecar was written before `path_for` / `start_clip` · **Fixed**: written after
  `start_clip`.

## 🔵 Nice to Have

- Spec paragraph rewrapped · **Fixed**.
- `_raise` annotated `NoReturn` · **Fixed**.
- Sequence note on the fault and release paths · **Fixed**.
- Verify round: the retried flush ran before rotation, so a full disk could stay in FAULT ·
  **Fixed**: rotation first.
- Verify round: a failed sidecar write in `close()` skipped `audio.close()` · **Fixed**: flush
  after both releases.
- Verify round: state diagram note missed the `close()` case · **Fixed**.
- Verify round (unverified): `start_clip` raising after the adapter closed the old output dates
  its end up to 1 s late · **Declined**: encoder failure only, within one tick.
- Wall clock vs monotonic timer on an NTP step during the ring (unverified) · **Declined**: clock
  steps are spec A4, out of scope.

## Out of scope (pre-existing)

- `Picamera2Recorder._release()` leaves a pending close timer after a camera loss.
- `_abandon_segments` drops an open clip without a sidecar.
- Spec says "monotonic clock"; `SystemClock` is wall time.
