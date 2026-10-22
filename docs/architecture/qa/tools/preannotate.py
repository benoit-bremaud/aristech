"""Zero-shot boxes (Grounding DINO tiny, Apache-2.0) for iNaturalist photos; class from taxon.

Usage: python -I preannotate.py <repo_root> <sheet_dir>
Writes data/external/inat-*/train/labels/<stem>.txt (YOLO, canonical classes) and review
contact sheets (12 overlays per sheet, numbered) into <sheet_dir>.
"""

import csv
import sys
from pathlib import Path

import torch
from PIL import Image, ImageDraw
from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor

MODEL = "IDEA-Research/grounding-dino-tiny"
PROMPT = "insect."
BOX_T, TEXT_T = 0.35, 0.25


def canonical(taxon: str) -> int:
    if taxon.startswith("Vespa velutina"):
        return 0
    if taxon.startswith("Vespa crabro"):
        return 1
    return 3


root, sheets = Path(sys.argv[1]), Path(sys.argv[2])
sheets.mkdir(parents=True, exist_ok=True)
with (root / "data/registry/inat-attribution.csv").open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
processor = AutoProcessor.from_pretrained(MODEL)
model = AutoModelForZeroShotObjectDetection.from_pretrained(MODEL).to("cuda")
thumbs: list[Image.Image] = []
index = open(sheets / "index.csv", "w", encoding="utf-8")
index.write("n,stem,source,class,boxes\n")
for n, row in enumerate(sorted(rows, key=lambda r: (r["source"], int(r["photo_id"])))):
    stem = f"{row['observation_id']}_{row['photo_id']}"
    image_path = root / "data/external" / row["source"] / "train/images" / f"{stem}.jpg"
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, text=PROMPT, return_tensors="pt").to("cuda")
    with torch.no_grad():
        out = model(**inputs)
    res = processor.post_process_grounded_object_detection(
        out, inputs.input_ids, threshold=BOX_T, text_threshold=TEXT_T,
        target_sizes=[image.size[::-1]],
    )[0]
    cls = canonical(row["taxon"])
    w, h = image.size
    lines, boxes = [], res["boxes"].tolist()
    # drop a box covering almost the whole frame when smaller boxes exist (frame-level false hit)
    if len(boxes) > 1:
        boxes = [b for b in boxes if (b[2] - b[0]) * (b[3] - b[1]) < 0.9 * w * h]
    for x0, y0, x1, y1 in boxes:
        lines.append(f"{cls} {(x0 + x1) / 2 / w:.6f} {(y0 + y1) / 2 / h:.6f} {(x1 - x0) / w:.6f} {(y1 - y0) / h:.6f}")
    label = image_path.parent.parent / "labels" / f"{stem}.txt"
    label.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    index.write(f"{n},{stem},{row['source']},{cls},{len(lines)}\n")
    thumb = image.copy()
    draw = ImageDraw.Draw(thumb)
    for x0, y0, x1, y1 in boxes:
        draw.rectangle([x0, y0, x1, y1], outline=(255, 0, 0), width=max(2, w // 150))
    thumb.thumbnail((320, 320))
    canvas = Image.new("RGB", (320, 340), "white")
    canvas.paste(thumb, (0, 20))
    ImageDraw.Draw(canvas).text((4, 4), f"#{n} c{cls} b{len(lines)}", fill=(0, 0, 0))
    thumbs.append(canvas)
    if len(thumbs) == 12 or n == len(rows) - 1:
        sheet = Image.new("RGB", (320 * 4, 340 * 3), "white")
        for i, t in enumerate(thumbs):
            sheet.paste(t, ((i % 4) * 320, (i // 4) * 340))
        sheet.save(sheets / f"sheet_{n // 12:03d}.jpg", quality=80)
        thumbs = []
index.close()
print("done", len(rows))
