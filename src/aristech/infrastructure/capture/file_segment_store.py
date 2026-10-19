"""`SegmentStore` on a local disk: `<root>/<kind>/<YYYY-MM-DD>/<kind>_<start>.<ext>` + `.json`."""

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

from aristech.domain import SegmentMetadata

_EXTENSIONS = {"audio": "flac", "video": "mp4"}
_SIDECAR = ".json"
_log = logging.getLogger("aristech.capture")


class FileSegmentStore:
    """Segments and JSON sidecars under `root` (the NVMe SSD on the rig)."""

    def __init__(self, root: Path) -> None:
        """`root` is created if missing."""
        self._root = root
        self._nothing_to_rotate = False
        self._active: set[Path] = set()
        root.mkdir(parents=True, exist_ok=True)

    def path_for(self, kind: str, start: datetime) -> str:
        """A new path; raise `ValueError` for an unknown kind."""
        if kind not in _EXTENSIONS:
            raise ValueError(f"unknown segment kind: {kind!r}")
        folder = self._root / kind / start.strftime("%Y-%m-%d")
        folder.mkdir(parents=True, exist_ok=True)
        stamp = start.strftime("%Y%m%dT%H%M%S%fZ")
        path = folder / f"{kind}_{stamp}.{_EXTENSIONS[kind]}"
        self._active.add(path)
        return str(path)

    def write_sidecar(self, path: str, metadata: SegmentMetadata) -> None:
        """Write `<path>.json` next to the segment."""
        self._nothing_to_rotate = False
        self._active.discard(Path(path))
        Path(path + _SIDECAR).write_text(json.dumps(metadata.to_dict(), indent=2), "utf-8")

    def free_fraction(self) -> float:
        """Free space of the filesystem holding `root`."""
        usage = shutil.disk_usage(self._root)
        return usage.free / usage.total

    def delete_oldest_unflagged(self) -> bool:
        """Delete the oldest non-flagged segment, sidecar start first, else file time.

        A segment without a readable sidecar (power cut, corrupt JSON) is dated by its file
        time and is never flagged, so orphans are rotated too. Segments still being written
        (handed out by `path_for`, no sidecar yet) are never candidates. The "nothing left"
        answer is cached until the next sidecar, so a full disk is not rescanned every tick.
        """
        if self._nothing_to_rotate:
            return False
        candidates: list[tuple[datetime, Path]] = []
        for extension in _EXTENSIONS.values():
            for media in self._root.rglob("*." + extension):
                if media in self._active:
                    continue
                start = self._unflagged_start(media)
                if start is not None:
                    candidates.append((start, media))
        if not candidates:
            self._nothing_to_rotate = True
            return False
        _, media = min(candidates)
        media.unlink(missing_ok=True)
        Path(str(media) + _SIDECAR).unlink(missing_ok=True)
        return True

    @staticmethod
    def _unflagged_start(media: Path) -> datetime | None:
        sidecar = Path(str(media) + _SIDECAR)
        try:
            data = json.loads(sidecar.read_text("utf-8"))
            if data.get("flagged", False):
                return None
            return datetime.fromisoformat(str(data["start_utc"]))
        except (OSError, ValueError, KeyError):
            _log.debug("no readable sidecar for %s; using its file time", media)
            return datetime.fromtimestamp(media.stat().st_mtime, tz=timezone.utc)
