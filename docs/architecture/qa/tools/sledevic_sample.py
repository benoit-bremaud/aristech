"""Download an evenly spaced sample of the Sledevic detection set (public API), verify sha256.

Usage: python -I sledevic_sample.py <out_dir> <folders.json>
Writes <out_dir>/train/images/<hive>_<frame>.jpg and train/labels/<hive>_<frame>.txt.
"""

import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

API = "https://data.mendeley.com/public-api/datasets/8gb9r2yhfc"
PER_HIVE = 188


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "aristech-dataset/0.1"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except OSError:
            if attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))
    raise AssertionError


def files(folder_id: str) -> list[dict]:
    return json.loads(get(f"{API}/files?folder_id={folder_id}&version=6"))


def fetch(entry: dict, target: Path) -> None:
    if target.exists():
        return
    body = get(entry["content_details"]["download_url"])
    if hashlib.sha256(body).hexdigest() != entry["content_details"]["sha256_hash"]:
        raise SystemExit(f"sha256 mismatch: {entry['filename']}")
    target.write_bytes(body)


out = Path(sys.argv[1])
folders = json.loads(Path(sys.argv[2]).read_text())
by_id = {f["id"]: f for f in folders}
detection = next(f["id"] for f in folders if f["name"] == "detection" and not f.get("parent_id"))
for hive_dir in sorted((f for f in folders if f.get("parent_id") == detection), key=lambda f: f["name"]):
    hive = hive_dir["name"].lstrip("_").removeprefix("bee_")
    sub = {f["name"]: f["id"] for f in folders if f.get("parent_id") == hive_dir["id"]}
    images = sorted(files(sub["images"]), key=lambda e: e["filename"])
    labels = {Path(e["filename"]).stem: e for e in files(sub["labels"])}
    step = max(1, len(images) // PER_HIVE)
    picked = [e for e in images[::step] if Path(e["filename"]).stem in labels][:PER_HIVE]
    for e in picked:
        stem = Path(e["filename"]).stem
        name = f"{hive}_{stem.removeprefix(hive)}"
        (out / "train" / "images").mkdir(parents=True, exist_ok=True)
        (out / "train" / "labels").mkdir(parents=True, exist_ok=True)
        fetch(e, out / "train" / "images" / f"{name}.jpg")
        fetch(labels[stem], out / "train" / "labels" / f"{name}.txt")
    print(hive, len(images), "frames,", len(picked), "kept, step", step, flush=True)
