"""Manifest import, group keys, merge, CSV round-trip (spec annotation-pipeline AC2–4, AC6, A3)."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from aristech.datasets.manifest import (
    CANONICAL_CLASSES,
    ManifestRow,
    Split,
    group_for_capture,
    group_key,
    import_yolo_source,
    merge_rows,
    read_manifest,
    remap_labels,
    write_manifest,
)
from aristech.datasets.registry import Source
from aristech.domain.capture import SegmentMetadata

_ROBO = Source("robo", "R", "u", "1", "CC-BY-4.0", "by X", "2026-10-19", group_rule="video")


def _export(root: Path, files: dict[str, tuple[bytes, str | None]]) -> Path:
    for rel, (pixels, label) in files.items():
        split, name = rel.split("/")
        (root / split / "images").mkdir(parents=True, exist_ok=True)
        (root / split / "labels").mkdir(parents=True, exist_ok=True)
        (root / split / "images" / name).write_bytes(pixels)
        if label is not None:
            (root / split / "labels" / f"{Path(name).stem}.txt").write_text(label, encoding="utf-8")
    return root


@pytest.mark.parametrize(
    ("rule", "stem", "expected"),
    [
        ("stem", "MAH00001_000003_jpg.rf.3d6d622e", "robo/MAH00001_000003"),
        ("video", "MAH00001_000003_jpg.rf.3d6d622e", "robo/MAH00001"),
        ("video", "Vespa-crabro-Germany-4_12_png.rf.abc", "robo/Vespa-crabro-Germany-4"),
        ("stem", "plain_photo", "robo/plain_photo"),
    ],
)
def test_group_key(rule: str, stem: str, expected: str) -> None:
    source = Source("robo", "R", "u", "1", "CC-BY-4.0", "x", "d", group_rule=rule)
    assert group_key(source, stem) == expected


def test_group_for_capture_is_hive_and_utc_day() -> None:
    meta = SegmentMetadata(
        rig_id="c1-home",
        hive_id="hive-3",
        site="home",
        kind="video",
        trigger="motion",
        start_utc=datetime(2027, 8, 14, 9, 30, tzinfo=timezone.utc),
        end_utc=datetime(2027, 8, 14, 9, 31, tzinfo=timezone.utc),
        clock_source="ntp",
        software_version="0.1.0",
    )
    assert group_for_capture(meta) == "own/hive-3/2027-08-14"


def test_remap_labels_swaps_ids_and_rejects_unmapped() -> None:
    assert remap_labels(["0 0.5 0.5 0.1 0.1", "", "1 0.2 0.2 0.1 0.1"], {0: 1, 1: 0}) == [
        "1 0.5 0.5 0.1 0.1",
        "0 0.2 0.2 0.1 0.1",
    ]
    with pytest.raises(ValueError, match=r"unmapped source classes: \[7\]"):
        remap_labels(["7 0.5 0.5 0.1 0.1"], {0: 1})
    with pytest.raises(ValueError, match="outside"):
        remap_labels(["0 0.5 0.5 0.1 0.1"], {0: 9})
    with pytest.raises(ValueError, match="malformed"):
        remap_labels(["0.0 0.5 0.5 0.1 0.1"], {0: 1})


def test_canonical_class_order_is_fixed() -> None:
    assert CANONICAL_CLASSES == ("vespa_velutina", "vespa_crabro", "apis_mellifera", "other")


def test_import_error_names_the_label_file(tmp_path: Path) -> None:
    root = _export(tmp_path / "export", {"train/a.jpg": (b"a", "5 0.5 0.5 0.1 0.1\n")})
    with pytest.raises(ValueError, match=r"a\.txt: unmapped"):
        import_yolo_source(_ROBO, root, {0: 1}, tmp_path / "store")


def test_import_hashes_remaps_and_dedups(tmp_path: Path) -> None:
    root = _export(
        tmp_path / "export",
        {
            "train/MAH1_000001_jpg.rf.aa.jpg": (b"img-a", "0 0.5 0.5 0.1 0.1\n"),
            "valid/MAH1_000002_jpg.rf.bb.jpg": (b"img-b", None),
            "test/MAH1_000003_jpg.rf.cc.jpg": (b"img-a", "0 0.5 0.5 0.1 0.1\n"),
            "train/notes.txt": (b"x", None),
        },
    )
    store = tmp_path / "store"
    rows = merge_rows([], import_yolo_source(_ROBO, root, {0: 1, 1: 0}, store))
    assert len(rows) == 2
    assert {r.group for r in rows} == {"robo/MAH1"}
    labelled = next(r for r in rows if r.classes)
    assert labelled.classes == ("vespa_crabro",)
    assert (store / "labels" / f"{labelled.image_sha256}.txt").read_text() == "1 0.5 0.5 0.1 0.1\n"
    assert (store / "images" / f"{labelled.image_sha256}.jpg").read_bytes() == b"img-a"
    assert next(r for r in rows if not r.classes).split is Split.UNASSIGNED


def _row(sha: str, group: str, split: Split = Split.UNASSIGNED, label: str = "l") -> ManifestRow:
    return ManifestRow(
        sha, group.split("/")[0], f"{sha}.jpg", group, label, ("vespa_velutina",), split
    )


def test_duplicate_inside_one_import_joins_both_groups(tmp_path: Path) -> None:
    root = _export(
        tmp_path / "export",
        {
            "train/A_000001.jpg": (b"same", None),
            "train/B_000001.jpg": (b"same", None),
            "train/B_000002.jpg": (b"b2", None),
        },
    )
    rows = merge_rows([], import_yolo_source(_ROBO, root, {0: 0}, tmp_path / "store"))
    assert len(rows) == 2 and len({r.group for r in rows}) == 1


def test_merge_joins_every_group_sharing_an_image() -> None:
    existing = [_row("a", "s1/g1", Split.TEST), _row("b", "s1/g2", Split.TRAIN)]
    incoming = [_row("a", "s2/x"), _row("b", "s2/x"), _row("c", "s2/x")]
    groups = {r.group for r in merge_rows(existing, incoming)}
    assert groups == {"s1/g1"}


def test_capture_frame_goes_through_the_same_manifest_path(tmp_path: Path) -> None:
    meta = SegmentMetadata(
        rig_id="c1",
        hive_id="hive-1",
        site="home",
        kind="video",
        trigger="motion",
        start_utc=datetime(2027, 8, 14, 23, 59, tzinfo=timezone.utc),
        end_utc=datetime(2027, 8, 15, 0, 1, tzinfo=timezone.utc),
        clock_source="ntp",
        software_version="0.1.0",
    )
    frame = ManifestRow("f1", "own-c1", "clip.mp4#0", group_for_capture(meta), "l", ())
    path = tmp_path / "manifest.csv"
    write_manifest(path, merge_rows([], [frame]))
    assert read_manifest(path)[0].group == "own/hive-1/2027-08-14"


def test_merge_keeps_known_split_and_joins_overlapping_groups() -> None:
    existing = [_row("a", "s1/g1", Split.TEST)]
    incoming = [_row("a", "s2/x", label="new"), _row("b", "s2/x"), _row("c", "s2/y")]
    merged = {r.image_sha256: r for r in merge_rows(existing, incoming)}
    assert merged["a"].split is Split.TEST and merged["a"].group == "s1/g1"
    assert merged["a"].label_sha256 == "new"
    assert merged["b"].group == "s1/g1"
    assert merged["c"].group == "s2/y"


def test_manifest_round_trip_and_missing_file(tmp_path: Path) -> None:
    path = tmp_path / "registry" / "manifest.csv"
    assert read_manifest(path) == []
    rows = [
        _row("b", "s/g", Split.TRAIN),
        ManifestRow("a", "s", "a.jpg", "s/g", "l", (), Split.TEST),
    ]
    write_manifest(path, rows)
    assert read_manifest(path) == sorted(rows, key=lambda r: r.image_sha256)


def test_duplicate_image_with_conflicting_labels_is_refused(tmp_path: Path) -> None:
    root = _export(
        tmp_path / "export",
        {
            "train/A_1.jpg": (b"same", "0 0.5 0.5 0.1 0.1\n"),
            "train/B_1.jpg": (b"same", "1 0.5 0.5 0.1 0.1\n"),
        },
    )
    with pytest.raises(ValueError, match="different labels"):
        import_yolo_source(_ROBO, root, {0: 0, 1: 1}, tmp_path / "store")
