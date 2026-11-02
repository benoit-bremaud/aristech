# ADR-0032: Telegram bot as the push channel of the attack alert

- Status: Accepted
- Date: 2026-11-02 (issue #152, attack-alert gate)
- Complements: ADR-0006 (faults pushed), ADR-0013 (one alert per episode), ADR-0031 (episode rule)

## Context

ADR-0031 built the attack episode rule, but its single alert only reaches the log. The beekeeper
must get it on their phone while the attack lasts, never one push per detection (spec
attack-alert AC5). The channel must keep secrets out of the repository, survive a network outage
(spec A1) and never stop the detection loop when it fails (spec A3, ADR-0006 fault path).

## Options (MCDA)

Criteria and weights: privacy and GDPR 25, delivery reliability 20, simplicity (stdlib only) 20,
phone experience 15, cost and operations 10, secrets 10. Scores 0–5; totals and sensitivity
computed by `mcda/adr_0032_push_channel.py` (all 53 130 weight vectors in steps of 5).

| Option | Privacy | Reliability | Simplicity | Phone | Cost | Secrets | Total /500 |
|---|---|---|---|---|---|---|---|
| A. Telegram bot (`sendMessage` over HTTPS) | 3 | 4 | 5 | 5 | 4 | 4 | **410** |
| B. ntfy, self-hosted | 5 | 3 | 4 | 4 | 3 | 4 | 395 |
| C. Email (SMTP) | 3 | 3 | 3 | 2 | 4 | 3 | 295 |

- A: a third party sees the alert time and counts; one HTTPS POST with `urllib`; instant phone
  notification; one token and one chat id.
- B: no third party, but a home server and its TLS to run and keep up.
- C: spam filters and delays; a mailbox is not a push.

Sensitivity: A first in 79 % of weight vectors, B 23 %, C 0 %. With privacy at 35, B passes A
(445 against 440). The pushed content is minimal (time, counts, no image, no location, no
personal data), which keeps A's privacy cost low. **Chosen: A** (owner, 2026-11-02).

## Decision

- `TelegramNotifier` decorates the log `Notifier`: every event is still logged, and only
  `notify_attack_started` and `notify_attack_ended` are pushed. No new port.
- Secrets come from the environment only: `ARISTECH_TELEGRAM_TOKEN`, `ARISTECH_TELEGRAM_CHAT_ID`
  (optional `ARISTECH_TELEGRAM_API_URL` for a self-hosted Bot API server, https only). The CLI
  enables the channel with `--push telegram` and refuses to start when a secret is missing.
- **A3**: a failed push is logged as `FAULT push channel` at ERROR, with the token masked, and
  never raised.
- **A1**: an unsent message waits in an in-memory queue (50 messages at most, oldest dropped) and
  is sent, prefixed `[delayed]`, before the next push that gets through.

## Consequences

- The queue lives in memory: a restart while offline loses it (the log keeps the episode). A
  persistent queue, the hive id and a representative frame come with the embedded deployment (M6).
- Telegram (a third party) receives alert times and counts; switch to option B if that becomes
  unacceptable — the adapter is one file behind the same `Notifier` port.
- Fault and heartbeat pushes of ADR-0006 can reuse the same adapter later.
