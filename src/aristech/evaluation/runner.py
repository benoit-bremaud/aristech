"""Run a `HornetDetector` over a YOLO-format dataset and score it.

Pairs each image with its YOLO label file, runs the detector, parses the
labels as ground-truth `Annotation`s, and aggregates into an
`EvaluationReport`. The detector and the image reader are **injected**, so the
orchestration is unit-tested with fakes (no torch / cv2); running VespAI on a
real dataset is integration.

Expected layout (Roboflow YOLOv5 export): ``<dataset>/<split>/images/*.jpg``
and ``<dataset>/<split>/labels/*.txt``.
"""

from collections.abc import Callable, Iterator, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path

from aristech.application.ports import HornetDetector
from aristech.domain import Species, VideoFrame
from aristech.evaluation.metrics import EvaluationReport, Sample, evaluate
from aristech.evaluation.yolo import parse_yolo_labels

# (pixels, width, height) — pixels is an opaque image array (numpy/cv2).
ImageReader = Callable[[Path], tuple[object, int, int]]

_IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".bmp")


def _default_image_reader(path: Path) -> tuple[object, int, int]:
    import cv2

    image = cv2.imread(str(path))
    if image is None:
        raise RuntimeError(f"could not read image: {path}")
    height, width = image.shape[:2]
    return image, int(width), int(height)


def _split_samples(
    detector: HornetDetector,
    split_dir: Path,
    class_map: Mapping[int, Species],
    reader: ImageReader,
    timestamp: datetime,
) -> Iterator[Sample]:
    images_dir = split_dir / "images"
    labels_dir = split_dir / "labels"
    if not images_dir.is_dir():
        return
    for image_path in sorted(images_dir.iterdir()):
        if image_path.suffix.lower() not in _IMAGE_SUFFIXES:
            continue
        pixels, width, height = reader(image_path)
        frame = VideoFrame(pixels=pixels, width=width, height=height, timestamp=timestamp)
        predictions = list(detector.detect(frame))
        label_file = labels_dir / f"{image_path.stem}.txt"
        lines = label_file.read_text(encoding="utf-8").splitlines() if label_file.exists() else []
        yield predictions, parse_yolo_labels(lines, width, height, class_map)


def evaluate_on_dataset(
    detector: HornetDetector,
    dataset_dir: Path | str,
    class_map: Mapping[int, Species],
    *,
    splits: Sequence[str] = ("test",),
    iou_threshold: float = 0.5,
    confidence_threshold: float = 0.0,
    image_reader: ImageReader | None = None,
    timestamp: datetime | None = None,
) -> EvaluationReport:
    """Score `detector` over the given `splits` of a YOLO dataset.

    `class_map` maps the dataset's integer class ids to `Species` (e.g.
    ``{0: VESPA_CRABRO, 1: VESPA_VELUTINA}``). Returns one aggregated
    `EvaluationReport` across all listed splits.
    """
    base = Path(dataset_dir)
    reader = image_reader or _default_image_reader
    ts = timestamp or datetime.now(timezone.utc)
    samples: list[Sample] = []
    for split in splits:
        samples.extend(_split_samples(detector, base / split, class_map, reader, ts))
    return evaluate(
        samples,
        iou_threshold=iou_threshold,
        confidence_threshold=confidence_threshold,
    )
