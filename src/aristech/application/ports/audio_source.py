from collections.abc import Iterator
from typing import Protocol

from aristech.domain import AudioSample


class AudioSource(Protocol):
    def samples(self) -> Iterator[AudioSample]: ...
    def close(self) -> None: ...
