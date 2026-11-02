"""`Notifier` adapter that pushes the attack alert and its summary to a Telegram chat
(ADR-0032), plus the heartbeat and the faults (ADR-0033). Everything is still logged by
the wrapped notifier; a detection is never pushed (spec attack-alert AC5). Stdlib only.
"""

import json
import logging
import os
import urllib.parse
import urllib.request
from collections import deque
from collections.abc import Callable, Mapping
from http.client import HTTPException

from aristech.application.attack_episode import AttackEpisode
from aristech.application.health import Fault, Heartbeat
from aristech.application.ports import Notifier
from aristech.domain import Detection

_log = logging.getLogger("aristech.notify")

TOKEN_ENV = "ARISTECH_TELEGRAM_TOKEN"
CHAT_ID_ENV = "ARISTECH_TELEGRAM_CHAT_ID"
# Optional: a self-hosted Bot API server, or a local stub for the gate run.
API_URL_ENV = "ARISTECH_TELEGRAM_API_URL"
DEFAULT_API_URL = "https://api.telegram.org"
# Messages kept while the channel is down (spec A1); the oldest are dropped beyond it.
MAX_PENDING = 50
# Short: a push runs inside the detection loop, so a dead network stalls it this long.
_TIMEOUT_S = 3.0

Send = Callable[[str], None]


def http_sender(token: str, chat_id: str, api_url: str = DEFAULT_API_URL) -> Send:
    """Return a function that posts one text message with the Bot API `sendMessage`."""
    parts = urllib.parse.urlsplit(api_url)
    local_stub = parts.scheme == "http" and parts.hostname == "127.0.0.1"
    if parts.username or parts.password or not (parts.scheme == "https" or local_stub):
        raise ValueError("the Telegram API URL must be https (or http://127.0.0.1 for a stub)")
    url = f"{api_url.rstrip('/')}/bot{token}/sendMessage"

    def send(text: str) -> None:
        body = json.dumps({"chat_id": chat_id, "text": text}).encode()
        request = urllib.request.Request(  # noqa: S310 — scheme checked above
            url, data=body, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(request, timeout=_TIMEOUT_S) as response:  # noqa: S310  # nosemgrep
            response.read(4096)

    return send


class TelegramNotifier:
    """Decorates a `Notifier`: delegates every event, and pushes episode start and end,
    the heartbeat and the faults.

    A failed push is logged as a fault and never raised (spec A3): the detection loop
    keeps running. The message is queued and sent, flagged as delayed, before the next
    push that gets through (spec A1).
    """

    def __init__(self, inner: Notifier, send: Send, secret: str = "") -> None:
        self._inner = inner
        self._send = send
        self._secret = secret
        self._pending: deque[str] = deque(maxlen=MAX_PENDING)

    @classmethod
    def from_env(cls, inner: Notifier, env: Mapping[str, str] = os.environ) -> "TelegramNotifier":
        """Build from the environment; secrets are never read from the config file."""
        token, chat_id = env.get(TOKEN_ENV, ""), env.get(CHAT_ID_ENV, "")
        if not token or not chat_id:
            raise ValueError(f"{TOKEN_ENV} and {CHAT_ID_ENV} must be set for the Telegram push")
        api_url = env.get(API_URL_ENV) or DEFAULT_API_URL
        return cls(inner, http_sender(token, chat_id, api_url), secret=token)

    def notify_detection(self, detection: Detection) -> None:
        """Log only: a detection is never pushed (AC5)."""
        self._inner.notify_detection(detection)

    def notify_abstention(self, detection: Detection) -> None:
        """Log only."""
        self._inner.notify_abstention(detection)

    def notify_attack_started(self, episode: AttackEpisode) -> None:
        """Log, then push the single alert of the episode."""
        self._inner.notify_attack_started(episode)
        self._push(
            f"Hornet attack under way since {episode.started:%Y-%m-%d %H:%M:%S} "
            f"({episode.peak} hit frame(s) in the window)."
        )

    def notify_attack_ended(self, episode: AttackEpisode) -> None:
        """Log, then push the episode summary."""
        self._inner.notify_attack_ended(episode)
        end = f"{episode.ended:%H:%M:%S}" if episode.ended else "?"
        self._push(
            f"Hornet attack ended: {episode.started:%Y-%m-%d %H:%M:%S} -> {end}, "
            f"peak {episode.peak}, {episode.hit_frames} hit frame(s)."
        )

    def notify_heartbeat(self, heartbeat: Heartbeat) -> None:
        """Log, then push the alive message."""
        self._inner.notify_heartbeat(heartbeat)
        self._push(
            f"Unit alive at {heartbeat.at:%Y-%m-%d %H:%M %Z}, up since "
            f"{heartbeat.up_since:%Y-%m-%d %H:%M %Z}: {heartbeat.frames} frame(s), "
            f"{heartbeat.episodes} attack episode(s)."
        )

    def notify_fault(self, fault: Fault) -> None:
        """Log, then push the fault kind, never its traceback."""
        self._inner.notify_fault(fault)
        muted = f" ({fault.suppressed} more muted since the last one)" if fault.suppressed else ""
        self._push(f"Unit fault at {fault.at:%Y-%m-%d %H:%M:%S %Z}: {fault.kind.value}{muted}.")

    def _push(self, text: str) -> None:
        while self._pending:
            if not self._deliver(f"[delayed] {self._pending[0]}"):
                self._pending.append(text)
                return
            self._pending.popleft()
        if not self._deliver(text):
            self._pending.append(text)

    def _deliver(self, text: str) -> bool:
        # Any channel failure is a fault, never a crash (spec A3); logged outside the
        # handler so no traceback, which could carry request details, reaches the log.
        try:
            self._send(text)
            return True
        except (OSError, HTTPException, ValueError) as exc:
            failure = f"{type(exc).__name__} ({exc})"
        # Urllib error messages carry no URL today; the mask guards the token if one ever does.
        if self._secret:
            failure = failure.replace(self._secret, "***")
        _log.error("FAULT push channel: %s; %d message(s) queued", failure, len(self._pending) + 1)
        return False
