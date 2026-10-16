"""`VespAIDetector` loading and inference, with hand-written fake `torch` and
`cv2` modules injected at the import boundary — no weights, no GPU needed."""

import sys
import types
from collections import namedtuple
from collections.abc import Callable
from datetime import datetime

import pytest

from aristech.domain import Species, VideoFrame
from aristech.infrastructure.vision.vespai_detector import VespAIDetector

_Row = namedtuple("_Row", "name confidence xmin ymin xmax ymax")


class _Table:
    def __init__(self, rows: list[_Row]) -> None:
        self._rows = rows

    def itertuples(self) -> list[_Row]:
        return self._rows


class _Results:
    def __init__(self, rows: list[_Row]) -> None:
        self.xyxy = [_Table(rows)]

    def pandas(self) -> "_Results":
        return self


class _FakeModel:
    def __init__(self, rows: list[_Row]) -> None:
        self.conf: float | None = None
        self.inputs: list[object] = []
        self._rows = rows

    def __call__(self, image: object) -> _Results:
        self.inputs.append(image)
        return _Results(self._rows)


class _FakeTorch(types.ModuleType):
    """Records the kwargs `torch.load` sees while `hub.load` runs."""

    def __init__(self, hub_load: Callable[..., object]) -> None:
        super().__init__("torch")
        self.load_kwargs: list[dict[str, object]] = []
        self.hub_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
        self.load = self._original_load
        self.hub = types.SimpleNamespace(load=self._hub_load)
        self._hub_impl = hub_load

    def _original_load(self, *args: object, **kwargs: object) -> str:
        self.load_kwargs.append(kwargs)
        return "checkpoint"

    def _hub_load(self, *args: object, **kwargs: object) -> object:
        self.hub_calls.append((args, kwargs))
        self.load("w.pt")
        return self._hub_impl()


_ROWS = [
    _Row("Vespa velutina", 0.9, 1.0, 2.0, 11.0, 22.0),
    _Row("Vespa crabro", 0.6, 0.0, 0.0, 5.0, 5.0),
    _Row("Apis mellifera", 0.4, 0.0, 0.0, 1.0, 1.0),
]


@pytest.fixture
def fake_cv2(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    cv2 = types.ModuleType("cv2")
    cv2.COLOR_BGR2RGB = 4  # type: ignore[attr-defined]  # fake module attribute
    cv2.cvtColor = lambda pixels, code: ("rgb", pixels, code)  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "cv2", cv2)
    return cv2


def _install_torch(monkeypatch: pytest.MonkeyPatch, model_factory: Callable[[], object]):
    torch = _FakeTorch(model_factory)
    monkeypatch.setitem(sys.modules, "torch", torch)
    return torch


def _frame() -> VideoFrame:
    return VideoFrame(pixels="bgr", width=64, height=48, timestamp=datetime(2026, 10, 16))


def test_load_relaxes_weights_only_then_restores_torch_load(monkeypatch):
    torch = _install_torch(monkeypatch, lambda: _FakeModel([]))
    original = torch.load

    VespAIDetector("w.pt", "yolov5", confidence=0.2)._load()

    assert torch.load_kwargs == [{"weights_only": False}]
    assert torch.load == original


def test_load_restores_torch_load_when_hub_load_fails(monkeypatch):
    def boom() -> object:
        raise RuntimeError("bad checkpoint")

    torch = _install_torch(monkeypatch, boom)
    original = torch.load

    with pytest.raises(RuntimeError, match="bad checkpoint"):
        VespAIDetector("w.pt", "yolov5")._load()

    assert torch.load == original


def test_load_passes_paths_and_sets_confidence_once(monkeypatch):
    model = _FakeModel([])
    torch = _install_torch(monkeypatch, lambda: model)
    detector = VespAIDetector("w.pt", "yolov5", confidence=0.2)

    assert detector._load() is detector._load() is model

    assert len(torch.hub_calls) == 1
    args, kwargs = torch.hub_calls[0]
    assert args == ("yolov5", "custom")
    assert kwargs["path"] == "w.pt"
    assert kwargs["source"] == "local"
    assert model.conf == 0.2


def test_detect_converts_bgr_and_maps_every_box(monkeypatch, fake_cv2):
    model = _FakeModel(_ROWS)
    _install_torch(monkeypatch, lambda: model)

    detections = VespAIDetector("w.pt", "yolov5").detect(_frame())

    assert model.inputs == [("rgb", "bgr", fake_cv2.COLOR_BGR2RGB)]
    assert [d.species for d in detections] == [
        Species.VESPA_VELUTINA,
        Species.VESPA_CRABRO,
        Species.UNKNOWN,
    ]
    first = detections[0]
    assert (first.bbox.x, first.bbox.y, first.bbox.width, first.bbox.height) == (1, 2, 10, 20)
    assert first.confidence == 0.9
    assert first.timestamp == datetime(2026, 10, 16)
