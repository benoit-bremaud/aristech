# Local review — aristech (#180, flush the ring into the open clip on shutdown)

- Date: 2026-11-06
- Scope: branch diff `origin/dev...fix/180-flush-ring-shutdown` (`Picamera2Recorder.close()`
  keeps the clip's output on the ring and stops the encoder first, `RecordCampaign.close()` end
  date, `CameraRecorder.close()` contract, tests, sequence and state diagrams)
- Option chosen by MCDA (computed by script, stable under ±10 on every weight): let the encoder
  stop flush the ring [445/500] over waiting for the pending close timer [370] and the status
  quo [325]
- Checks run: adversarial review (findings, verify) · `mise x -- just check`
- Verdict: push gate open after round 2 · Must 1 (fixed) · Should 4 (fixed) · Nice 6 (5 fixed, 1 noted)

## Pre-push checks

| Step | Result |
|---|---|
| Tests | ✅ `just check` green; coverage above the 80 % floor |
| Security | ✅ semgrep, osv, gitleaks clean |

## Upstream facts (picamera2 source)

- `CircularOutput2.stop()` flushes the whole ring into the attached output, then stops it;
  `close_output()` detaches the output and drops what is left.
- `Encoder.stop()` stops each of its outputs; `Picamera2.stop_recording()` stops the camera
  before the encoder, so a camera error there skipped the flush and left the file unfinished.

## 🔴 Must Have

- `record_campaign.py` · `close()` dated the end of any pending closing clip at the release,
  including one whose output had already closed (ring elapsed before the next tick, or a sidecar
  write retried), so the sidecar claimed footage the file does not have · **Fixed**: only a clip
  stopped less than one ring before is moved to the release; a test keeps the stop time once the
  ring has elapsed. Port, use case, adapter and diagram wording qualified the same way.

## 🟡 Should Have

- `picamera2_recorder.py` · finishing the clip's file depended on `stop_recording()`, which
  stops the camera first; errors were logged at debug · **Fixed**: release in three steps
  (`stop_encoder`, `stop`, `close`), each in its own `try`, logged at warning; a test fails
  `camera.stop` and the clip is still flushed and finished.
- Tests never exercised a pending close already finishing the file, and the fakes accepted a
  double stop · **Fixed**: a test blocks the file's `stop` and checks that `close()` waits for
  it and stops once; the fake ring raises on a second stop or a close without output, as
  upstream.
- Review report missing · **Fixed**: this file.

## 🔵 Nice to Have

- Comment on the timer join gave the wrong reason · **Fixed**: the timer is a daemon thread,
  joined so the process does not exit while the file is being finished.
- Redundant `_clip_open = False` in `close()` · **Fixed**: removed (`_release` sets it).
- Test asserted a private attribute · **Fixed**: removed, behaviour asserts kept.
- Sequence diagram released audio before the camera, unlike the code · **Fixed**: order swapped.

## Verify round (round 2)

- All round-1 findings fixed; the encoder-then-camera stop order is safe upstream (the encoder
  ignores frames once stopped).
- Should · the reopen-with-failed-sidecar case had no test · **Fixed**: test added (the end stays
  at the ring front).
- Nice · the fake camera's `close()` did not stop it first, as upstream does · **Fixed**.
- Nice · the sequence diagram showed the audio sidecar after the camera release · **Fixed**.
- Nice · a close racing the pending close within tens of ms could date a sidecar late
  (unmeasured) · **Noted**: fix only if bench data shows it (needs a port change).

## Hosted review (round 3)

- A clip closed by a camera loss was flushed when the adapter released the camera, yet a
  shutdown within one ring moved its end to the release · **Fixed**: the closing clip carries
  `on_ring`, False after a camera loss (alone or with the audio, the FAULT branch) or once a
  sidecar write was attempted (its output has closed); only a clip still on the ring is
  extended; tests cover both loss branches. The port now states that `healthy()` False after
  a loss means the camera was released, and the rule reads the same in the port, use case and
  diagrams. Verify round 4: push gate open, two wording Nice fixed.
- The release end is read before the audio close and the encoder stop, so the file may hold a
  few frames past it · **Kept**: the sidecar then never claims footage the file lacks, the same
  precision as the stop-tick rule; an exact end needs the encoder's last frame time (port change).

## Out of scope (follow-ups)

- #190: `_close_pending_now()` racing a pending close already firing when the next clip opens.
- #184: the pending close timer outlives a camera loss and closes the released ring.
- #185: a clip abandoned on FAULT gets no sidecar.
