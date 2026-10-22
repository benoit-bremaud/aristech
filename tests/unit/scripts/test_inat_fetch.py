"""Unit tests for scripts/inat_fetch.py: licence filter and attribution file (spec AC10, A8)."""

import importlib.util
import json
import sys
import urllib.parse
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).parents[3] / "scripts" / "inat_fetch.py"
_spec = importlib.util.spec_from_file_location("inat_fetch", _SCRIPT)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _mod  # dataclasses resolve their module by name
_spec.loader.exec_module(_mod)


def _photo(photo_id: int, code: str | None, hidden: bool = False) -> dict[str, object]:
    return {
        "id": photo_id,
        "license_code": code,
        "hidden": hidden,
        "attribution": f"(c) X, {code}",
        "url": f"https://static.example/photos/{photo_id}/square.jpg",
    }


def test_only_cc_by_and_cc0_photos_are_kept() -> None:
    obs = {
        "id": 42,
        "taxon": {"name": "Vespa velutina"},
        "photos": [
            _photo(1, "cc-by"),
            _photo(2, "cc-by-nc"),
            _photo(3, "cc0"),
            _photo(4, None),
            _photo(5, "cc-by-nd"),
            _photo(6, "cc-by", hidden=True),
        ],
    }
    rows = list(_mod.photo_rows([obs]))
    assert [(r.photo_id, r.source) for r in rows] == [(1, "inat-cc-by"), (3, "inat-cc0")]
    assert rows[0].file_name == "42_1.jpg"
    assert rows[0].url.endswith("/1/large.jpg")
    assert rows[0].taxon == "Vespa velutina"


def test_observation_without_photos_yields_nothing() -> None:
    assert list(_mod.photo_rows([{"id": 1, "taxon": None, "photos": None}])) == []


def test_page_url_filters_research_grade_and_licences() -> None:
    url = _mod.page_url(119019, 2)
    assert "taxon_id=119019" in url and "quality_grade=research" in url
    assert "photo_license=cc-by%2Ccc0" in url and "page=2" in url


def test_attribution_round_trip_is_sorted(tmp_path: Path) -> None:
    path = tmp_path / "registry" / "inat-attribution.csv"
    rows = list(_mod.photo_rows([{"id": 7, "taxon": {"name": "T"}, "photos": [_photo(9, "cc0")]}]))
    rows += list(
        _mod.photo_rows([{"id": 8, "taxon": {"name": "T"}, "photos": [_photo(3, "cc-by")]}])
    )
    _mod.write_attribution(path, rows)
    assert [r.photo_id for r in _mod.read_attribution(path)] == [3, 9]
    assert _mod.read_attribution(tmp_path / "missing.csv") == []


def test_fetch_skips_known_photos_and_respects_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pages = {
        1: {
            "results": [
                {
                    "id": 1,
                    "taxon": {"name": "T"},
                    "photos": [_photo(10, "cc-by"), _photo(11, "cc0")],
                },
                {"id": 2, "taxon": {"name": "T"}, "photos": [_photo(12, "cc-by")]},
            ]
        },
        2: {"results": []},
    }

    def fake_get(url: str) -> bytes:
        if "api.inaturalist.org" in url:
            page = int(urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["page"][0])
            return json.dumps(pages[page]).encode()
        return b"pixels"

    monkeypatch.setattr(_mod, "_get", fake_get)
    attribution = tmp_path / "attr.csv"
    _mod.write_attribution(attribution, list(_mod.photo_rows([pages[1]["results"][0]]))[:1])
    added = _mod.fetch(119019, 1, tmp_path / "ext", attribution)
    assert added == 1
    assert (
        tmp_path / "ext" / "inat-cc0" / "train" / "images" / "1_11.jpg"
    ).read_bytes() == b"pixels"
    assert [r.photo_id for r in _mod.read_attribution(attribution)] == [10, 11]
