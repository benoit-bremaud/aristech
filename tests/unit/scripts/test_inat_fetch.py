"""Unit tests for scripts/inat_fetch.py: licence filter and attribution file (spec AC10, A8)."""

import importlib.util
import json
import sys
import urllib.error
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
    url = _mod.page_url(119019, 42)
    assert "taxon_id=119019" in url and "quality_grade=research" in url
    assert "photo_license=cc-by%2Ccc0" in url and "id_above=42" in url


def test_attribution_round_trip_is_sorted(tmp_path: Path) -> None:
    path = tmp_path / "registry" / "inat-attribution.csv"
    rows = list(_mod.photo_rows([{"id": 7, "taxon": {"name": "T"}, "photos": [_photo(9, "cc0")]}]))
    rows += list(
        _mod.photo_rows([{"id": 8, "taxon": {"name": "T"}, "photos": [_photo(3, "cc-by")]}])
    )
    _mod.write_attribution(path, rows)
    assert [r.photo_id for r in _mod.read_attribution(path)] == [3, 9]
    assert _mod.read_attribution(tmp_path / "missing.csv") == []


def _api(pages: dict[int, list[dict[str, object]]], fail: set[int] | None = None):
    """Fake `_get`: API pages keyed by `id_above`; photo URLs in `fail` raise URLError."""

    def fake_get(url: str) -> bytes:
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname == "api.inaturalist.org":
            id_above = int(urllib.parse.parse_qs(parsed.query)["id_above"][0])
            return json.dumps({"results": pages.get(id_above, [])}).encode()
        if fail and any(f"/{p}/" in url for p in fail):
            raise urllib.error.URLError("boom")
        return b"pixels"

    return fake_get


def _obs(obs_id: int, *photos: dict[str, object]) -> dict[str, object]:
    return {"id": obs_id, "taxon": {"name": "T"}, "photos": list(photos)}


def test_fetch_skips_known_photos_and_respects_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = _obs(1, _photo(10, "cc-by"), _photo(11, "cc0"))
    monkeypatch.setattr(_mod, "_get", _api({0: [first, _obs(2, _photo(12, "cc-by"))]}))
    attribution = tmp_path / "attr.csv"
    _mod.write_attribution(attribution, list(_mod.photo_rows([first]))[:1])
    assert _mod.fetch(119019, 1, tmp_path / "ext", attribution) == 1
    image = tmp_path / "ext" / "inat-cc0" / "train" / "images" / "1_11.jpg"
    assert image.read_bytes() == b"pixels"
    assert [r.photo_id for r in _mod.read_attribution(attribution)] == [10, 11]


def test_fetch_follows_id_pages_until_a_short_page(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_mod, "PER_PAGE", 2)
    pages = {0: [_obs(1, _photo(10, "cc-by")), _obs(2)], 2: [_obs(3, _photo(30, "cc0"))]}
    monkeypatch.setattr(_mod, "_get", _api(pages))
    attribution = tmp_path / "attr.csv"
    assert _mod.fetch(1, 10, tmp_path / "ext", attribution) == 2
    assert [r.photo_id for r in _mod.read_attribution(attribution)] == [10, 30]


def test_failed_photo_is_skipped_and_rows_survive_a_crash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pages = {0: [_obs(1, _photo(10, "cc-by"), _photo(11, "cc-by"), _photo(12, "cc0"))]}
    monkeypatch.setattr(_mod, "_get", _api(pages, fail={11}))
    attribution = tmp_path / "attr.csv"
    assert _mod.fetch(1, 10, tmp_path / "ext", attribution) == 2
    assert [r.photo_id for r in _mod.read_attribution(attribution)] == [10, 12]
    assert not list((tmp_path / "ext").rglob("*.part"))

    def api_down(url: str) -> bytes:
        raise urllib.error.URLError("down")

    monkeypatch.setattr(_mod, "_get", api_down)
    with pytest.raises(urllib.error.URLError):
        _mod.fetch(1, 10, tmp_path / "ext", attribution)
    assert [r.photo_id for r in _mod.read_attribution(attribution)] == [10, 12]
