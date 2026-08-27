#!/usr/bin/env python3
"""Build a comparison board from three direction preview images."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    for name in names:
        path = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / name
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default(size=size)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directions", required=True)
    parser.add_argument("--previews-dir", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    data = json.loads(Path(args.directions).read_text(encoding="utf-8"))
    directions = data["directions"]
    preview_dir = Path(args.previews_dir)
    width = 1800
    outer = 58
    gap = 26
    card_width = (width - outer * 2 - gap * 2) // 3
    image_height = 320
    card_height = 500
    board = Image.new("RGB", (width, outer * 2 + card_height), "#ECEAE4")
    draw = ImageDraw.Draw(board)

    for index, direction in enumerate(directions):
        x = outer + index * (card_width + gap)
        y = outer
        preview_path = preview_dir / direction["id"] / "github-social.jpg"
        if not preview_path.exists():
            raise SystemExit(f"Missing direction preview: {preview_path}")
        preview = ImageOps.contain(
            Image.open(preview_path).convert("RGB"),
            (card_width, image_height),
            Image.Resampling.LANCZOS,
        )
        preview_frame = Image.new("RGB", (card_width, image_height), "#111318")
        preview_frame.paste(
            preview,
            ((card_width - preview.width) // 2, (image_height - preview.height) // 2),
        )
        board.paste(preview_frame, (x, y))
        draw.text(
            (x, y + image_height + 22),
            direction["name"],
            font=font(28, True),
            fill="#111318",
        )
        brand = direction["brand"]
        for chip_index, color in enumerate(
            (brand["background"], brand["primary"], brand["secondary"])
        ):
            chip_x = x + chip_index * 42
            chip_y = y + image_height + 70
            draw.rounded_rectangle(
                (chip_x, chip_y, chip_x + 30, chip_y + 30), radius=8, fill=color
            )
        rationale = direction["rationale"]
        words = rationale.split()
        lines: list[str] = []
        current = ""
        body_font = font(17)
        while words:
            candidate = f"{current} {words[0]}".strip()
            if draw.textbbox((0, 0), candidate, font=body_font)[2] <= card_width:
                current = candidate
                words.pop(0)
            else:
                lines.append(current)
                current = ""
        if current:
            lines.append(current)
        draw.multiline_text(
            (x, y + image_height + 116),
            "\n".join(lines[:3]),
            font=body_font,
            fill="#45454A",
            spacing=5,
        )

    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    board.save(destination, "PNG", optimize=True)
    print(f"Wrote {destination.resolve()} ({board.width}x{board.height})")


if __name__ == "__main__":
    main()
