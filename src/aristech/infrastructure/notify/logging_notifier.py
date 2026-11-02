"""`Notifier` adapter that logs each detection via the standard logging
module. No external dependency — the default sink for v1 (detection +
alert). Richer channels (MQTT, Telegram) come later as separate adapters.
"""

import logging

from aristech.application.attack_episode import AttackEpisode
from aristech.application.health import Fault, Heartbeat
from aristech.domain import Detection

_log = logging.getLogger("aristech.detection")


class LoggingNotifier:
    """Logs to the `aristech.detection` logger at INFO."""

    def notify_detection(self, detection: Detection) -> None:
        """Log species, confidence, centre and timestamp of a threat."""
        c = detection.bbox.center
        _log.info(
            "detection %s conf=%.2f threat=%s at (%.0f,%.0f) %s",
            detection.species.value,
            detection.confidence,
            detection.is_threat(),
            c.x,
            c.y,
            detection.timestamp.isoformat(),
        )

    def notify_abstention(self, detection: Detection) -> None:
        """Log a target seen below the operating threshold."""
        c = detection.bbox.center
        _log.info(
            "abstain %s conf=%.2f below operating threshold at (%.0f,%.0f) %s",
            detection.species.value,
            detection.confidence,
            c.x,
            c.y,
            detection.timestamp.isoformat(),
        )

    def notify_attack_started(self, episode: AttackEpisode) -> None:
        """Log the single alert of an attack episode, at WARNING so it stands out."""
        _log.warning(
            "ATTACK ALERT episode started %s (%d hit frame(s) in the window)",
            episode.started.isoformat(),
            episode.peak,
        )

    def notify_attack_ended(self, episode: AttackEpisode) -> None:
        """Log the episode summary: start, end, peak and total hit frames."""
        _log.info(
            "attack episode ended %s -> %s peak=%d hit_frames=%d",
            episode.started.isoformat(),
            episode.ended.isoformat() if episode.ended else "?",
            episode.peak,
            episode.hit_frames,
        )

    def notify_heartbeat(self, heartbeat: Heartbeat) -> None:
        """Log that the unit is alive, with its uptime and work done."""
        _log.info(
            "heartbeat up since %s frames=%d episodes=%d",
            heartbeat.up_since.isoformat(),
            heartbeat.frames,
            heartbeat.episodes,
        )

    def notify_fault(self, fault: Fault) -> None:
        """Log a fault at ERROR, with the count of same-kind faults muted before it."""
        _log.error(
            "FAULT %s: %s (%d muted since the last push)",
            fault.kind.value,
            fault.detail,
            fault.suppressed,
        )
