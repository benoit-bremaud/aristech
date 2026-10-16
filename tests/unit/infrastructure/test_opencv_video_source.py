import pytest


def test_reads_frames_from_a_generated_video(tmp_path):
    cv2 = pytest.importorskip("cv2")
    np = pytest.importorskip("numpy")

    from aristech.infrastructure.vision.opencv_video_source import OpenCVVideoSource

    path = str(tmp_path / "tiny.mp4")
    width, height = 64, 48
    writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), 5.0, (width, height))
    for _ in range(3):
        writer.write(np.zeros((height, width, 3), dtype=np.uint8))
    writer.release()

    source = OpenCVVideoSource(path)
    frames = list(source.frames())
    source.close()

    assert len(frames) == 3
    assert frames[0].width == width
    assert frames[0].height == height


def test_open_failure_raises(tmp_path):
    pytest.importorskip("cv2")
    from aristech.infrastructure.vision.opencv_video_source import OpenCVVideoSource

    source = OpenCVVideoSource(str(tmp_path / "does-not-exist.mp4"))
    with pytest.raises(RuntimeError, match="could not open"):
        list(source.frames())
