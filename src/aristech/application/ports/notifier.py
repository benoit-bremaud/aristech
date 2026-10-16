"""Notification port."""

from typing import Protocol

from aristech.domain import Detection


class Notifier(Protocol):
    """Reports decisions to the outside world (log, message, dashboard)."""

    def notify_detection(self, detection: Detection) -> None:
        """A target at or above the operating threshold: the system would act."""
        ...

    def notify_abstention(self, detection: Detection) -> None:
        """A target seen below the operating threshold: not acted on (ADR-0009)."""
        ...
