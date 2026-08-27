#!/usr/bin/env python3
"""Build a labeled contact sheet from the six repo-visuals outputs."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


FILES = (
    ("README HERO · 1600 × 900", "readme-hero.png"),
    ("GITHUB SOCIAL · 1280 × 640", "github-social.jpg"),
    ("RELEASE CARD · 1200 × 675", "release-card.png"),
    ("PRODUCT GALLERY · 1270 × 760", "product-gallery.png"),
    ("LAUNCH POST · 1200 × 1500", "launch-post.jpg"),
    ("COMMUNITY SQUARE · 1080 × 1080", "community-square.png"),
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    missing = [name for _, name in FILES if not (input_dir / name).exists()]
    if missing:
        raise SystemExit(f"Missing assets: {', '.join(missing)}")

    sheet_width = 1600
    card_width = 720
    preview_height = 405
    label_height = 58
    gap = 36
    outer = 62
    columns = 2
    rows = 3
    sheet_height = outer * 2 + rows * (preview_height + label_height) + (rows - 1) * gap
    sheet = Image.new("RGB", (sheet_width, sheet_height), "#F4F4F5")
    draw = ImageDraw.Draw(sheet)
    label_font = load_font(22)

    for index, (label, filename) in enumerate(FILES):
        column = index % columns
        row = index // columns
        x = outer + column * (card_width + gap)
        y = outer + row * (preview_height + label_height + gap)
        source = Image.open(input_dir / filename).convert("RGB")
        thumb = ImageOps.contain(source, (card_width, preview_height), Image.Resampling.LANCZOS)
        frame = Image.new("RGB", (card_width, preview_height), "#111318")
        frame.paste(
            thumb,
            ((card_width - thumb.width) // 2, (preview_height - thumb.height) // 2),
        )
        sheet.paste(frame, (x, y))
        draw.text((x, y + preview_height + 16), label, font=label_font, fill="#18181B")

    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination, "PNG", optimize=True)
    print(f"Wrote {destination.resolve()} ({sheet.width}x{sheet.height})")


if __name__ == "__main__":
    main()
