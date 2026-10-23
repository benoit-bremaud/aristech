"""Licence register: every image source with its licence (ADR-0019, spec annotation-pipeline AC1).

`data/registry/licences.csv` is committed; a source whose licence is not in the allow-list can
never be imported, so only commercially compatible data reaches a product training set.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

ALLOWED_LICENCES = frozenset({"CC-BY-4.0", "CC-BY-SA-4.0", "CC0-1.0", "own"})
"""SPDX ids (plus `own` for our captures) allowed into the database; never NC."""

GROUP_RULES = frozenset({"observation", "stem", "video"})
"""How an image's group key is derived from its file name (see `manifest.group_key`)."""

_FIELDS = (
    "id",
    "name",
    "url",
    "version",
    "licence",
    "attribution",
    "retrieved",
    "group_rule",
    "captive",
)


class LicenceError(ValueError):
    """A source is unknown or its licence is not in `ALLOWED_LICENCES`."""


@dataclass(frozen=True, slots=True)
class Source:
    """One dataset source: where it comes from, under which licence, how to group its images."""

    id: str
    name: str
    url: str
    version: str
    licence: str
    attribution: str
    retrieved: str
    group_rule: str = "stem"
    captive: bool = False


def load_register(path: Path) -> dict[str, Source]:
    """Read `licences.csv` into sources by id; raises `ValueError` on a malformed row."""
    sources: dict[str, Source] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("group_rule") not in GROUP_RULES:
                raise ValueError(
                    f"{row.get('id')}: group_rule must be one of {sorted(GROUP_RULES)}"
                )
            if row["id"] in sources:
                raise ValueError(f"duplicate source id {row['id']!r}")
            sources[row["id"]] = Source(
                **{k: row[k] for k in _FIELDS if k != "captive"},
                captive=(row.get("captive") or "").strip().lower() == "true",
            )
    return sources


def require(sources: dict[str, Source], source_id: str) -> Source:
    """Return the source if it may be imported; raise `LicenceError` otherwise."""
    source = sources.get(source_id)
    if source is None:
        raise LicenceError(f"source {source_id!r} is not in the licence register")
    if source.licence not in ALLOWED_LICENCES:
        raise LicenceError(
            f"source {source_id!r} has licence {source.licence!r}, "
            f"allowed: {', '.join(sorted(ALLOWED_LICENCES))}"
        )
    return source
