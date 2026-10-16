from typing import Protocol

from aristech.domain import Detection


class Notifier(Protocol):
    def notify_detection(self, detection: Detection) -> None: ...

    def notify_abstention(self, detection: Detection) -> None:
        """A target seen below the operating threshold: not acted on (ADR-0009)."""
        ...
