# Local review — aristech (issue #152, attack alert push channel)

- Date: 2026-11-02
- Scope: branch diff `dev...feat/152-push-channel`
- Checks run: `just gate` (lint, format, mypy, typos, actionlint, zizmor, tests, semgrep, osv,
  gitleaks, SonarQube) · code review of the diff (correctness, security, dependency rule, tests,
  docs)
- Verdict: ship · Must 1 (fixed) · Should 3 (3 fixed) · Nice 3 (3 fixed)

## Pre-merge gate

| Step | Result |
|---|---|
| 1 Tests | ✅ 339 passed, 2 skipped, 5 deselected (integration) |
| 2 Coverage | ✅ ≥ 96 % (floor 80) |
| 3 SonarQube | ✅ quality gate passed (4 new issues fixed: chained `startswith`, `noqa` syntax, two `logging.exception` hints answered by logging outside the handler) |
| 4 Secrets | ✅ gitleaks clean · diff read: no token, checkpoint or video committed; `.env.example` has empty values |
| 5 QA pass | ✅ CLI with RF-DETR Small on an 80-s sample clip (10 s hornets, 70 s empty) and `--push telegram` against a local Bot API stub: exactly 1 alert and 1 summary received; stub stopped: 2 `FAULT push channel` errors, run finished with exit 0; token absent from the log |

## 🔴 Must Have (fixed)
- The API URL check used `startswith("http://127.0.0.1")`, so `http://127.0.0.1.evil.com` or
  `http://127.0.0.1@evil.com` would send the token in clear to a remote host → parsed with
  `urlsplit` (https, or http on host 127.0.0.1 without credentials), bypass tests added.

## 🟠 Should Have (fixed)
- Synchronous push could stall the detection loop 10 s per event on a dead network → timeout 3 s,
  stall recorded in ADR-0032 and the gate risks; background sender deferred to M6.
- The stdlib sender test compared the message text with itself → asserts the text.
- The queue-bound test did not check the `[delayed]` replays → asserted.

## 🟢 Nice to Have (fixed)
- `response.read()` unbounded → `read(4096)`.
- Token masking relies on urllib messages carrying no URL → comment added.
- CLI test now clears both secrets, independent of the developer's environment.
