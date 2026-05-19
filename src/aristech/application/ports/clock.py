from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Indirection sur `datetime.now()` pour rendre les use cases testables."""

    def now(self) -> datetime: ...
