"""Licence register: allow-list and parsing (spec annotation-pipeline AC1)."""

from pathlib import Path

import pytest

from aristech.datasets.registry import LicenceError, load_register, require

_HEADER = "id,name,url,version,licence,attribution,retrieved,group_rule,captive\n"


def _register(tmp_path: Path, *rows: str) -> Path:
    path = tmp_path / "licences.csv"
    path.write_text(_HEADER + "".join(f"{r}\n" for r in rows), encoding="utf-8")
    return path


def test_allowed_licence_is_returned(tmp_path: Path) -> None:
    sources = load_register(_register(tmp_path, "a,A,u,1,CC-BY-4.0,by X,2026-10-19,stem,false"))
    assert require(sources, "a").licence == "CC-BY-4.0"


@pytest.mark.parametrize("licence", ["CC-BY-NC-SA-4.0", "unknown", ""])
def test_non_allowed_licence_is_refused(tmp_path: Path, licence: str) -> None:
    sources = load_register(_register(tmp_path, f"a,A,u,1,{licence},x,2026-10-19,stem,false"))
    with pytest.raises(LicenceError, match="allowed"):
        require(sources, "a")


def test_unknown_source_is_refused(tmp_path: Path) -> None:
    with pytest.raises(LicenceError, match="not in the licence register"):
        require(load_register(_register(tmp_path)), "nope")


def test_captive_flag_and_group_rule(tmp_path: Path) -> None:
    sources = load_register(_register(tmp_path, "lab,L,u,1,own,us,2026-10-19,video,TRUE"))
    assert sources["lab"].captive and sources["lab"].group_rule == "video"


@pytest.mark.parametrize(
    "rows",
    [
        ("a,A,u,1,own,x,d,frames,false",),
        ("a,A,u,1,own,x,d,stem,false", "a,A,u,1,own,x,d,stem,false"),
    ],
)
def test_malformed_register_raises(tmp_path: Path, rows: tuple[str, ...]) -> None:
    with pytest.raises(ValueError):
        load_register(_register(tmp_path, *rows))


def test_committed_register_is_all_allowed() -> None:
    path = Path(__file__).parents[3] / "data" / "registry" / "licences.csv"
    sources = load_register(path)
    assert sources
    for source_id in sources:
        require(sources, source_id)
