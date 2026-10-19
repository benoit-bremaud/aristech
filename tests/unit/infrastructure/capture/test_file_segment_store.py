import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

from aristech.domain import SegmentMetadata
from aristech.infrastructure.capture import FileSegmentStore


def _metadata(start: datetime, flagged: bool = False) -> SegmentMetadata:
    return SegmentMetadata(
        rig_id="rig-1",
        hive_id="hive-a",
        site="home",
        kind="audio",
        trigger="continuous",
        start_utc=start,
        end_utc=start,
        clock_source="ntp",
        software_version="abc",
        flagged=flagged,
    )


def _segment(store: FileSegmentStore, hour: int, flagged: bool = False) -> Path:
    start = datetime(2026, 8, 15, hour, tzinfo=timezone.utc)
    path = store.path_for("audio", start)
    Path(path).write_bytes(b"x")
    store.write_sidecar(path, _metadata(start, flagged))
    return Path(path)


def test_path_is_dated_and_typed(tmp_path: Path) -> None:
    store = FileSegmentStore(tmp_path)

    path = store.path_for("video", datetime(2026, 8, 15, 9, 30, tzinfo=timezone.utc))

    assert path == str(tmp_path / "video" / "2026-08-15" / "video_20260815T093000000000Z.mp4")


def test_unknown_kind_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown segment kind"):
        FileSegmentStore(tmp_path).path_for("photo", datetime.now(timezone.utc))


def test_sidecar_is_json_next_to_segment(tmp_path: Path) -> None:
    segment = _segment(FileSegmentStore(tmp_path), 9)

    data = json.loads(Path(str(segment) + ".json").read_text("utf-8"))

    assert data["hive_id"] == "hive-a"


def test_rotation_deletes_oldest_unflagged_first(tmp_path: Path) -> None:
    store = FileSegmentStore(tmp_path)
    flagged = _segment(store, 8, flagged=True)
    oldest = _segment(store, 9)
    newest = _segment(store, 10)

    assert store.delete_oldest_unflagged() is True

    assert flagged.exists() and newest.exists()
    assert not oldest.exists() and not Path(str(oldest) + ".json").exists()


def test_rotation_with_nothing_unflagged_returns_false(tmp_path: Path) -> None:
    store = FileSegmentStore(tmp_path)
    _segment(store, 8, flagged=True)

    assert store.delete_oldest_unflagged() is False


def test_free_fraction_is_a_fraction(tmp_path: Path) -> None:
    assert 0.0 <= FileSegmentStore(tmp_path).free_fraction() <= 1.0


def test_orphan_segment_without_sidecar_is_rotated(tmp_path: Path) -> None:
    crashed_run = FileSegmentStore(tmp_path)
    orphan = Path(crashed_run.path_for("video", datetime(2026, 8, 15, 7, tzinfo=timezone.utc)))
    orphan.write_bytes(b"x")
    store = FileSegmentStore(tmp_path)
    os.utime(orphan, (0, 0))
    newer = _segment(store, 9)

    assert store.delete_oldest_unflagged() is True

    assert not orphan.exists() and newer.exists()


def test_corrupt_sidecar_does_not_break_rotation(tmp_path: Path) -> None:
    store = FileSegmentStore(tmp_path)
    segment = _segment(store, 9)
    Path(str(segment) + ".json").write_text("{not json", "utf-8")

    assert store.delete_oldest_unflagged() is True
    assert not segment.exists()


def test_nothing_to_rotate_is_cached_until_next_sidecar(tmp_path: Path) -> None:
    store = FileSegmentStore(tmp_path)
    assert store.delete_oldest_unflagged() is False

    _segment(store, 9)

    assert store.delete_oldest_unflagged() is True


def test_segment_being_written_is_never_rotated(tmp_path: Path) -> None:
    store = FileSegmentStore(tmp_path)
    active = Path(store.path_for("audio", datetime(2026, 8, 15, 7, tzinfo=timezone.utc)))
    active.write_bytes(b"x")

    assert store.delete_oldest_unflagged() is False
    assert active.exists()
