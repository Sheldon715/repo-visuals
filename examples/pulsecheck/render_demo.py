#!/usr/bin/env python3
"""Render the deliberately plain README state and a before/after comparison."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.ImageFont:
    if mono:
        names = ["CascadiaMono.ttf", "consola.ttf", "DejaVuSansMono.ttf"]
    elif bold:
        names = ["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]
    else:
        names = ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"]
    roots = [
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts",
        Path("/usr/share/fonts/truetype/dejavu"),
    ]
    for root in roots:
        for name in names:
            path = root / name
            if path.exists():
                return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default(size=size)


def render_before() -> Image.Image:
    image = Image.new("RGB", (1400, 900), "#0D1117")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((34, 34, 1366, 866), radius=18, fill="#161B22", outline="#30363D", width=2)
    draw.text((78, 70), "Sheldon715 / pulsecheck", font=font(24, True), fill="#58A6FF")
    draw.line((78, 118, 1320, 118), fill="#30363D", width=2)
    draw.text((92, 158), "Pulsecheck", font=font(54, True), fill="#F0F6FC")
    draw.text(
        (92, 240),
        "A tiny CLI that checks health endpoints and prints a clean status summary.",
        font=font(25),
        fill="#C9D1D9",
    )
    draw.text((92, 318), "Install", font=font(34, True), fill="#F0F6FC")
    draw.rounded_rectangle((92, 378, 930, 460), radius=10, fill="#0D1117")
    draw.text((118, 402), "npm install -g pulsecheck-cli", font=font(23, mono=True), fill="#C9D1D9")
    draw.text((92, 520), "Use", font=font(34, True), fill="#F0F6FC")
    draw.rounded_rectangle((92, 580, 1260, 695), radius=10, fill="#0D1117")
    draw.text((118, 606), "pulsecheck https://api.example.com/health", font=font(22, mono=True), fill="#C9D1D9")
    draw.text((118, 646), "           https://status.example.com/ping", font=font(22, mono=True), fill="#C9D1D9")
    draw.text((92, 748), "Useful, but visually indistinguishable from thousands of small repositories.", font=font(23), fill="#8B949E")
    return image


def build_comparison(before: Image.Image, after_path: Path) -> Image.Image:
    width, height = 1800, 860
    canvas = Image.new("RGB", (width, height), "#F5F3EC")
    draw = ImageDraw.Draw(canvas)
    draw.text((70, 48), "FROM REPOSITORY TO LAUNCH IDENTITY", font=font(34, True), fill="#14161B")
    draw.text((70, 96), "Pulsecheck · generated with repo-visuals", font=font(22), fill="#5D5F66")
    panel_width, panel_height = 800, 520
    before_fit = ImageOps.contain(before, (panel_width, panel_height), Image.Resampling.LANCZOS)
    after_fit = ImageOps.contain(
        Image.open(after_path).convert("RGB"),
        (panel_width, panel_height),
        Image.Resampling.LANCZOS,
    )
    for x, preview in ((70, before_fit), (930, after_fit)):
        frame = Image.new("RGB", (panel_width, panel_height), "#111318")
        frame.paste(
            preview,
            ((panel_width - preview.width) // 2, (panel_height - preview.height) // 2),
        )
        canvas.paste(frame, (x, 190))
    draw.text((70, 735), "BEFORE · README ONLY", font=font(24, True), fill="#66686F")
    draw.text((930, 735), "AFTER · LOCKED VISUAL SYSTEM", font=font(24, True), fill="#14161B")
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--after")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    before = render_before()
    before.save(out_dir / "before.png", "PNG", optimize=True)
    if args.after:
        comparison = build_comparison(before, Path(args.after))
        comparison.save(out_dir / "before-after.png", "PNG", optimize=True)
    print(f"Wrote demo assets to {out_dir.resolve()}")


if __name__ == "__main__":
    main()
