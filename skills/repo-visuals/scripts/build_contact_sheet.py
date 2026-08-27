#!/usr/bin/env python3
"""Build a labeled contact sheet from repo-visuals outputs."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


FILES = (
    ("README HERO · 1600 × 900", "readme-hero.png"),
    ("GITHUB SOCIAL · 1280 × 640", "github-social.jpg"),
    ("RELEASE CARD · 1200 × 675", "release-card.png"),
)


def load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "segoeuib.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/Library/Fonts/Arial Bold.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default(size=size)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    missing = [name for _, name in FILES if not (input_dir / name).exists()]
    if missing:
        raise SystemExit(f"Missing assets: {', '.join(missing)}")

    sheet_width = 1600
    card_width = 720
    image_height = 405
    label_height = 58
    gap = 36
    outer = 62
    positions = ((0, 0), (1, 0), (0, 1))
    rows = 2
    sheet_height = outer * 2 + rows * (image_height + label_height) + (rows - 1) * gap
    sheet = Image.new("RGB", (sheet_width, sheet_height), "#F4F4F5")
    draw = ImageDraw.Draw(sheet)
    font = load_font(22)

    for (label, filename), (column, row) in zip(FILES, positions, strict=True):
        x = outer + column * (card_width + gap)
        y = outer + row * (image_height + label_height + gap)
        source = Image.open(input_dir / filename).convert("RGB")
        thumb = ImageOps.fit(source, (card_width, image_height), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (x, y))
        draw.text((x, y + image_height + 16), label, font=font, fill="#18181B")

    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination, "PNG", optimize=True)
    print(f"Wrote {destination.resolve()} ({sheet.width}x{sheet.height})")


if __name__ == "__main__":
    main()
