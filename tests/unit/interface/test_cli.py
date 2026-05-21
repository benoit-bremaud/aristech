"""CLI composition-root tests. These exercise the argument-validation
branches that run before any vision adapter is imported, so they need
neither cv2 nor torch and run in CI."""

from pathlib import Path

from aristech.interface.cli.main import main


def _config(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.yaml"
    cfg.write_text("app:\n  version: test\n", encoding="utf-8")
    return cfg


def _common(tmp_path: Path) -> list[str]:
    # Point logging-config at a missing file → falls back to basicConfig.
    return ["--config", str(_config(tmp_path)), "--logging-config", str(tmp_path / "none.yaml")]


def test_no_video_is_a_noop(tmp_path):
    assert main(_common(tmp_path)) == 0


def test_video_without_weights_errors(tmp_path):
    assert main([*_common(tmp_path), "--video", "0"]) == 2


def test_out_of_range_confidence_errors_cleanly(tmp_path):
    rc = main(
        [
            *_common(tmp_path),
            "--video",
            "0",
            "--weights",
            "w.pt",
            "--yolov5-dir",
            "d",
            "--confidence",
            "1.5",
        ]
    )
    assert rc == 2


def test_missing_config_errors(tmp_path):
    assert main(["--config", str(tmp_path / "absent.yaml")]) == 2


def test_nonexistent_weights_errors(tmp_path):
    yolo = tmp_path / "yolo"
    yolo.mkdir()
    rc = main(
        [
            *_common(tmp_path),
            "--video",
            "0",
            "--weights",
            str(tmp_path / "missing.pt"),
            "--yolov5-dir",
            str(yolo),
        ]
    )
    assert rc == 2


def test_nonexistent_yolov5_dir_errors(tmp_path):
    weights = tmp_path / "w.pt"
    weights.write_text("x", encoding="utf-8")
    rc = main(
        [
            *_common(tmp_path),
            "--video",
            "0",
            "--weights",
            str(weights),
            "--yolov5-dir",
            str(tmp_path / "nodir"),
        ]
    )
    assert rc == 2
