import logging
from datetime import datetime

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
