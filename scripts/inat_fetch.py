"""Fetch iNaturalist research-grade photos licensed CC BY or CC0 (ADR-0023, spec AC10, A8).

Photos go to the git-ignored ``data/external/inat-<licence>/train/images/`` as
``<observation_id>_<photo_id>.jpg``; one attribution row per photo is appended to the committed
``data/registry/inat-attribution.csv``. Photos with any other licence are never downloaded.
Re-running skips photos already listed in the attribution file.

Example:
    python scripts/inat_fetch.py --taxon-id 119019 --limit 150
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sys
import time
import urllib.parse
import urllib.request
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import asdict, dataclass, fields
from pathlib import Path

API = "https://api.inaturalist.org/v1/observations"
USER_AGENT = "aristech-dataset/0.1 (https://github.com/benoit-bremaud/aristech)"
# iNaturalist licence code → register source id (also its directory under data/external/).
LICENCES = {"cc-by": "inat-cc-by", "cc0": "inat-cc0"}
PAUSE_SECONDS = 1.0
PER_PAGE = 200

log = logging.getLogger("inat_fetch")


@dataclass(frozen=True)
class PhotoRow:
    """One attribution row of ``inat-attribution.csv``."""

    photo_id: int
    observation_id: int
    taxon: str
    licence: str
    source: str
    attribution: str
    url: str

    @property
    def file_name(self) -> str:
        return f"{self.observation_id}_{self.photo_id}.jpg"


ATTRIBUTION_FIELDS = [f.name for f in fields(PhotoRow)]


def photo_rows(observations: Iterable[dict[str, object]]) -> Iterator[PhotoRow]:
    """Yield a row per allowed-licence photo of each observation; skip the rest (A8)."""
    for obs in observations:
        taxon = obs.get("taxon")
        taxon_name = str(taxon.get("name", "")) if isinstance(taxon, dict) else ""
        photos = obs.get("photos")
        for photo in photos if isinstance(photos, list) else []:
            code = photo.get("license_code")
            if code not in LICENCES or photo.get("hidden"):
                continue
            yield PhotoRow(
                photo_id=int(photo["id"]),
                observation_id=int(str(obs["id"])),
                taxon=taxon_name,
                licence=code,
                source=LICENCES[code],
                attribution=str(photo.get("attribution", "")),
                url=str(photo["url"]).replace("/square.", "/large."),
            )


def page_url(taxon_id: int, id_above: int) -> str:
    """Observations API query: research grade, CC BY / CC0 photos, ids above `id_above`, ascending.

    Keyset paging (`id_above`) avoids the API's 10,000-result page limit and shifting pages.
    """
    query = {
        "taxon_id": taxon_id,
        "quality_grade": "research",
        "photo_license": ",".join(LICENCES),
        "per_page": PER_PAGE,
        "id_above": id_above,
        "order_by": "id",
        "order": "asc",
    }
    return f"{API}?{urllib.parse.urlencode(query)}"


def read_attribution(path: Path) -> list[PhotoRow]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return [
            PhotoRow(
                photo_id=int(row["photo_id"]),
                observation_id=int(row["observation_id"]),
                taxon=row["taxon"],
                licence=row["licence"],
                source=row["source"],
                attribution=row["attribution"],
                url=row["url"],
            )
            for row in csv.DictReader(handle)
        ]


def write_attribution(path: Path, rows: Iterable[PhotoRow]) -> None:
    """Write rows sorted by photo id, so the committed file diffs cleanly."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ATTRIBUTION_FIELDS)
        writer.writeheader()
        writer.writerows(asdict(r) for r in sorted(rows, key=lambda r: r.photo_id))


def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310 (fixed https hosts)
        body: bytes = response.read()
    time.sleep(PAUSE_SECONDS)
    return body


def _download(row: PhotoRow, external: Path) -> bool:
    """Write one photo atomically; log and skip it when the download fails."""
    target = external / row.source / "train" / "images" / row.file_name
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        body = _get(row.url)
    except OSError as error:  # URLError, HTTPError and timeouts are all OSError
        log.warning("photo %d skipped: %s", row.photo_id, error)
        return False
    partial = target.with_suffix(".part")
    partial.write_bytes(body)
    os.replace(partial, target)
    return True


def fetch(taxon_id: int, limit: int, external: Path, attribution: Path) -> int:
    """Download up to `limit` new photos of `taxon_id`; return how many were added.

    The attribution file is written even if the run stops early, so every photo on disk keeps
    its row (AC10) and a re-run skips it.
    """
    known = read_attribution(attribution)
    seen = {r.photo_id for r in known}
    added: list[PhotoRow] = []
    last_id = 0
    try:
        while len(added) < limit:
            results = json.loads(_get(page_url(taxon_id, last_id))).get("results", [])
            for row in photo_rows(results):
                if len(added) >= limit:
                    break
                if row.photo_id not in seen and _download(row, external):
                    seen.add(row.photo_id)
                    added.append(row)
            if len(results) < PER_PAGE:
                break
            last_id = int(results[-1]["id"])
    finally:
        write_attribution(attribution, [*known, *added])
    return len(added)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--taxon-id", type=int, required=True)
    parser.add_argument("--limit", type=int, default=150)
    parser.add_argument("--external", type=Path, default=Path("data/external"))
    parser.add_argument(
        "--attribution", type=Path, default=Path("data/registry/inat-attribution.csv")
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    count = fetch(args.taxon_id, args.limit, args.external, args.attribution)
    log.info("taxon %d: %d photos added", args.taxon_id, count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
