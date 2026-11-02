import logging
from datetime import UTC, datetime

from aristech.application.health import Fault, FaultKind, Heartbeat
from aristech.domain import BoundingBox, Detection, Species
from aristech.infrastructure.notify.logging_notifier import LoggingNotifier


def test_logs_species_and_confidence(caplog):
    det = Detection(
        species=Species.VESPA_VELUTINA,
        bbox=BoundingBox(0, 0, 10, 10),
        confidence=0.9,
        timestamp=datetime(2026, 5, 21),
    )
    with caplog.at_level(logging.INFO, logger="aristech.detection"):
        LoggingNotifier().notify_detection(det)
    assert "vespa_velutina" in caplog.text
    assert "0.90" in caplog.text
    assert "threat=True" in caplog.text
    assert "abstain" not in caplog.text


def test_logs_abstention_distinctly(caplog):
    det = Detection(
        species=Species.VESPA_VELUTINA,
        bbox=BoundingBox(0, 0, 10, 10),
        confidence=0.42,
        timestamp=datetime(2026, 10, 16),
    )
    with caplog.at_level(logging.INFO, logger="aristech.detection"):
        LoggingNotifier().notify_abstention(det)
    assert "abstain vespa_velutina" in caplog.text
    assert "0.42" in caplog.text


def test_logs_attack_alert_and_episode_summary(caplog):
    from aristech.application.attack_episode import AttackEpisode

    started = AttackEpisode(started=datetime(2026, 11, 2, 12), hit_frames=3, peak=3)
    ended = AttackEpisode(started.started, 9, 5, ended=datetime(2026, 11, 2, 12, 5))
    with caplog.at_level(logging.INFO, logger="aristech.detection"):
        LoggingNotifier().notify_attack_started(started)
        LoggingNotifier().notify_attack_ended(ended)
        LoggingNotifier().notify_attack_ended(started)
    assert "ATTACK ALERT episode started 2026-11-02T12:00:00" in caplog.text
    assert "-> 2026-11-02T12:05:00 peak=5 hit_frames=9" in caplog.text
    assert "-> ? peak=3" in caplog.text


def test_logs_heartbeat(caplog):
    beat = Heartbeat(datetime(2026, 11, 3, tzinfo=UTC), datetime(2026, 11, 2, tzinfo=UTC), 7, 1)
    with caplog.at_level(logging.INFO, logger="aristech.detection"):
        LoggingNotifier().notify_heartbeat(beat)
    assert "heartbeat up since 2026-11-02T00:00:00+00:00 frames=7 episodes=1" in caplog.text


def test_logs_fault_at_error(caplog):
    fault = Fault(FaultKind.SOURCE_ENDED, datetime(2026, 11, 2, tzinfo=UTC), "camera gone", 2)
    with caplog.at_level(logging.ERROR, logger="aristech.detection"):
        LoggingNotifier().notify_fault(fault)
    assert caplog.records[0].levelno == logging.ERROR
    assert "FAULT source_ended: camera gone (2 muted since the last push)" in caplog.text
