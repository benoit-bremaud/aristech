"""Telegram push adapter (ADR-0032) with a hand-written fake channel; no network,
except the stdlib sender test, which talks to a local HTTP stub."""

import json
import logging
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from aristech.application.attack_episode import AttackEpisode
from aristech.domain import BoundingBox, Detection, Species
from aristech.infrastructure.notify.telegram_notifier import (
    MAX_PENDING,
    TelegramNotifier,
    http_sender,
)

STARTED = AttackEpisode(started=datetime(2026, 11, 2, 12), hit_frames=3, peak=3)
ENDED = AttackEpisode(STARTED.started, 9, 5, ended=datetime(2026, 11, 2, 12, 5))


class _FakeChannel:
    def __init__(self) -> None:
        self.sent: list[str] = []
        self.down = False

    def __call__(self, text: str) -> None:
        if self.down:
            raise OSError("network unreachable for bot-SECRET")
        self.sent.append(text)


class _RecordingNotifier:
    def __init__(self) -> None:
        self.events: list[str] = []

    def notify_detection(self, detection: Detection) -> None:
        self.events.append("detection")

    def notify_abstention(self, detection: Detection) -> None:
        self.events.append("abstention")

    def notify_attack_started(self, episode: AttackEpisode) -> None:
        self.events.append("started")

    def notify_attack_ended(self, episode: AttackEpisode) -> None:
        self.events.append("ended")


@pytest.fixture
def channel() -> _FakeChannel:
    return _FakeChannel()


@pytest.fixture
def inner() -> _RecordingNotifier:
    return _RecordingNotifier()


def test_episode_pushes_one_alert_and_one_summary(channel, inner):
    notifier = TelegramNotifier(inner, channel)
    notifier.notify_attack_started(STARTED)
    notifier.notify_attack_ended(ENDED)
    assert len(channel.sent) == 2
    assert channel.sent[0].startswith("Hornet attack under way since 2026-11-02 12:00:00")
    assert "peak 5, 9 hit frame(s)" in channel.sent[1]
    assert inner.events == ["started", "ended"]


def test_detections_are_logged_never_pushed(channel, inner):
    det = Detection(Species.VESPA_VELUTINA, BoundingBox(0, 0, 10, 10), 0.9, datetime(2026, 11, 2))
    notifier = TelegramNotifier(inner, channel)
    notifier.notify_detection(det)
    notifier.notify_abstention(det)
    assert channel.sent == []
    assert inner.events == ["detection", "abstention"]


def test_channel_failure_is_a_logged_fault_with_the_secret_masked(channel, inner, caplog):
    channel.down = True
    notifier = TelegramNotifier(inner, channel, secret="SECRET")
    with caplog.at_level(logging.ERROR, logger="aristech.notify"):
        notifier.notify_attack_started(STARTED)
    assert "FAULT push channel: OSError (network unreachable for bot-***)" in caplog.text
    assert "SECRET" not in caplog.text
    assert inner.events == ["started"]


def test_queued_message_is_sent_delayed_once_back_online(channel, inner):
    notifier = TelegramNotifier(inner, channel)
    channel.down = True
    notifier.notify_attack_started(STARTED)
    channel.down = False
    notifier.notify_attack_ended(ENDED)
    assert channel.sent[0].startswith("[delayed] Hornet attack under way")
    assert channel.sent[1].startswith("Hornet attack ended")
    assert len(channel.sent) == 2


def test_queue_keeps_order_while_down_and_is_bounded(channel, inner):
    notifier = TelegramNotifier(inner, channel)
    channel.down = True
    for _ in range(MAX_PENDING + 5):
        notifier.notify_attack_started(STARTED)
    channel.down = False
    notifier.notify_attack_ended(ENDED)
    assert len(channel.sent) == MAX_PENDING + 1
    assert all(m.startswith("[delayed] Hornet attack under way") for m in channel.sent[:-1])
    assert channel.sent[-1].startswith("Hornet attack ended")


def test_from_env_needs_token_and_chat_id(inner):
    with pytest.raises(ValueError, match="ARISTECH_TELEGRAM_TOKEN"):
        TelegramNotifier.from_env(inner, env={"ARISTECH_TELEGRAM_TOKEN": "t"})


@pytest.mark.parametrize(
    "url", ["http://example.org", "http://127.0.0.1.evil.com", "http://127.0.0.1@evil.com/"]
)
def test_sender_refuses_plain_http_to_a_remote_host(url):
    with pytest.raises(ValueError, match="https"):
        http_sender("t", "1", url)


def test_http_sender_posts_send_message_to_the_bot_api():
    received: list[tuple[str, dict[str, str]]] = []

    class _Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802 — http.server API
            length = int(self.headers["Content-Length"])
            received.append((self.path, json.loads(self.rfile.read(length))))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"ok": true}')

        def log_message(self, *args: object) -> None:
            pass

    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.handle_request)
    thread.start()
    env = {
        "ARISTECH_TELEGRAM_TOKEN": "tok",
        "ARISTECH_TELEGRAM_CHAT_ID": "42",
        "ARISTECH_TELEGRAM_API_URL": f"http://127.0.0.1:{server.server_port}",
    }
    TelegramNotifier.from_env(_RecordingNotifier(), env=env).notify_attack_started(STARTED)
    thread.join(timeout=5)
    server.server_close()
    assert [path for path, _ in received] == ["/bottok/sendMessage"]
    assert received[0][1]["chat_id"] == "42"
    assert received[0][1]["text"].startswith("Hornet attack under way")
