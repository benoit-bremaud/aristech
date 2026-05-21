"""`Notifier` adapter that logs each detection via the standard logging
module. No external dependency — the default sink for v1 (detection +
alert). Richer channels (MQTT, Telegram) come later as separate adapters.
"""

import logging

from aristech.domain import Detection

_log = logging.getLogger("aristech.detection")


class LoggingNotifier:
    def notify_detection(self, detection: Detection) -> None:
        c = detection.bbox.center
        _log.info(
            "threat %s conf=%.2f at (%.0f,%.0f) %s",
            detection.species.value,
            detection.confidence,
            c.x,
            c.y,
            detection.timestamp.isoformat(),
        )
