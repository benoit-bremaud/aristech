"""Build a contact sheet of iNaturalist boxes for a human spot check (issue #95, PR 4).

Picks ``--per-class`` images per class among the iNaturalist manifest rows (seeded),
draws each box with its class name and writes one JPEG grid plus the list of sampled
image hashes. The sheet holds third-party pixels: write it outside the repository.

Example:
    python docs/architecture/qa/tools/box_spot_check.py \\
        --dataset ../bold-blackwell-988e7c/data/dataset --out /tmp/spot
"""

import argparse
import csv
import random
from pathlib import Path

from PIL import Image, ImageDraw

CLASSES = ["vespa_velutina", "vespa_crabro", "apis_mellifera", "other"]
TILE = 320


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", default="data/registry/manifest.csv")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--per-class", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    with open(args.manifest, newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["source_id"].startswith("inat-")]
    rng = random.Random(args.seed)
    picked = []
    for name in ("vespa_velutina", "vespa_crabro", "other"):
        pool = sorted((r for r in rows if r["classes"] == name), key=lambda r: r["image_sha256"])
        picked += rng.sample(pool, min(args.per_class, len(pool)))

    dataset, out = Path(args.dataset), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cols = 6
    sheet = Image.new("RGB", (cols * TILE, -(-len(picked) // cols) * TILE), "white")
    for i, row in enumerate(picked):
        sha = row["image_sha256"]
        image = next((dataset / "images").glob(f"{sha}.*"))
        tile = Image.open(image).convert("RGB")
        draw = ImageDraw.Draw(tile)
        w, h = tile.size
        for line in (dataset / "labels" / f"{sha}.txt").read_text().splitlines():
            c, cx, cy, bw, bh = line.split()
            x0, y0 = (float(cx) - float(bw) / 2) * w, (float(cy) - float(bh) / 2) * h
            box = [x0, y0, x0 + float(bw) * w, y0 + float(bh) * h]
            draw.rectangle(box, outline="red", width=max(2, w // 150))
        tile.thumbnail((TILE - 8, TILE - 24))
        cell = Image.new("RGB", (TILE, TILE), "white")
        cell.paste(tile, (4, 20))
        ImageDraw.Draw(cell).text((4, 4), f"#{i + 1} {row['classes']}", fill="black")
        sheet.paste(cell, ((i % cols) * TILE, (i // cols) * TILE))
    sheet.save(out / "box-spot-check.jpg", quality=85)
    with open(out / "box-spot-check.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "image_sha256", "source_id", "source_path", "classes"])
        for i, r in enumerate(picked):
            writer.writerow([i + 1, r["image_sha256"], r["source_id"], r["source_path"], r["classes"]])


if __name__ == "__main__":
    main()
