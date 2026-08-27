#!/usr/bin/env python3
"""Compose exact repository launch assets over AI-generated artwork."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ASSETS = {
    "readme-hero": (1600, 900, "PNG"),
    "github-social": (1280, 640, "JPEG"),
    "release-card": (1200, 675, "PNG"),
}


def parse_hex(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Expected a six-digit hex color, got: {value!r}")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def font_candidates(bold: bool) -> list[Path]:
    names = (
        ["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]
        if bold
        else ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"]
    )
    roots = [
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts",
        Path("/usr/share/fonts/truetype/dejavu"),
        Path("/Library/Fonts"),
        Path.home() / "Library/Fonts",
    ]
    return [root / name for root in roots for name in names]


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in font_candidates(bold):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default(size=size)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
    max_lines: int,
) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words.pop(0)
    while words:
        candidate = f"{current} {words[0]}"
        if text_width(draw, candidate, font) <= max_width:
            current = candidate
            words.pop(0)
        else:
            lines.append(current)
            current = words.pop(0)
            if len(lines) == max_lines - 1:
                if words:
                    current = f"{current} {' '.join(words)}"
                    words = []
                break
    lines.append(current)

    if len(lines) > max_lines:
        lines = lines[:max_lines]
    if text_width(draw, lines[-1], font) > max_width:
        value = lines[-1]
        while value and text_width(draw, f"{value}…", font) > max_width:
            value = value[:-1].rstrip()
        lines[-1] = f"{value}…"
    return lines


def fit_title_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_lines: int,
    start_size: int,
    min_size: int,
) -> tuple[ImageFont.ImageFont, list[str]]:
    for size in range(start_size, min_size - 1, -2):
        font = load_font(size, bold=True)
        lines = wrap_text(draw, text, font, max_width, max_lines)
        if len(lines) <= max_lines and all(text_width(draw, line, font) <= max_width for line in lines):
            return font, lines
    font = load_font(min_size, bold=True)
    return font, wrap_text(draw, text, font, max_width, max_lines)


def add_contrast_overlay(image: Image.Image) -> Image.Image:
    width, height = image.size
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pixels = overlay.load()
    for x in range(width):
        ratio = x / max(width - 1, 1)
        alpha = int(225 * max(0.0, 1.0 - ratio / 0.78) ** 1.7)
        for y in range(height):
            pixels[x, y] = (3, 5, 12, alpha)
    return Image.alpha_composite(image.convert("RGBA"), overlay)


def draw_logo(
    canvas: Image.Image,
    logo_path: Path | None,
    position: tuple[int, int],
    max_size: int,
) -> int:
    if logo_path is None:
        return 0
    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    x, y = position
    canvas.alpha_composite(logo, (x, y))
    return logo.width + max(18, max_size // 5)


def render_asset(
    asset_id: str,
    background: Image.Image,
    manifest: dict[str, Any],
    logo_path: Path | None,
) -> Image.Image:
    width, height, _ = ASSETS[asset_id]
    base = ImageOps.fit(
        background.convert("RGB"),
        (width, height),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    ).filter(ImageFilter.GaussianBlur(radius=0.15))
    canvas = add_contrast_overlay(base)
    draw = ImageDraw.Draw(canvas)

    brand = manifest["brand"]
    copy = manifest["copy"]
    project = manifest["project"]
    foreground = parse_hex(brand["foreground"])
    primary = parse_hex(brand["primary"])
    secondary = parse_hex(brand["secondary"])

    margin_x = int(width * 0.075)
    margin_y = int(height * 0.11)
    text_width_limit = int(width * 0.49)
    scale = width / 1600

    accent_width = max(5, int(8 * scale))
    draw.rounded_rectangle(
        (margin_x, margin_y, margin_x + accent_width, margin_y + int(height * 0.11)),
        radius=accent_width // 2,
        fill=primary,
    )

    eyebrow = copy["release_label"] if asset_id == "release-card" else copy["eyebrow"]
    eyebrow_font = load_font(max(17, int(23 * scale)), bold=True)
    eyebrow_x = margin_x + accent_width + max(16, int(22 * scale))
    eyebrow_y = margin_y + int(height * 0.018)
    draw.text((eyebrow_x, eyebrow_y), eyebrow, font=eyebrow_font, fill=secondary)

    title_y = margin_y + int(height * 0.18)
    title_font, title_lines = fit_title_font(
        draw,
        copy["title"],
        text_width_limit,
        2,
        start_size=max(54, int(96 * scale)),
        min_size=max(36, int(58 * scale)),
    )
    title_spacing = max(5, int(8 * scale))
    title_box = draw.multiline_textbbox(
        (margin_x, title_y),
        "\n".join(title_lines),
        font=title_font,
        spacing=title_spacing,
    )
    draw.multiline_text(
        (margin_x, title_y),
        "\n".join(title_lines),
        font=title_font,
        fill=foreground,
        spacing=title_spacing,
    )

    subtitle_font = load_font(max(20, int(30 * scale)))
    subtitle_lines = wrap_text(
        draw,
        copy["subtitle"],
        subtitle_font,
        text_width_limit,
        3,
    )
    subtitle_y = title_box[3] + int(height * 0.055)
    draw.multiline_text(
        (margin_x, subtitle_y),
        "\n".join(subtitle_lines),
        font=subtitle_font,
        fill=(foreground[0], foreground[1], foreground[2], 205),
        spacing=max(7, int(11 * scale)),
    )

    footer_y = height - margin_y - max(42, int(56 * scale))
    logo_offset = draw_logo(
        canvas,
        logo_path,
        (margin_x, footer_y),
        max(38, int(52 * scale)),
    )
    repository_url = project.get("repository_url", "")
    if repository_url:
        repo_label = repository_url.removeprefix("https://").removeprefix("http://").rstrip("/")
    else:
        stack = project.get("tech_stack") or []
        repo_label = " · ".join(stack[:3]) or "OPEN SOURCE"
    footer_font = load_font(max(16, int(21 * scale)), bold=True)
    draw.text(
        (margin_x + logo_offset, footer_y + max(7, int(10 * scale))),
        repo_label,
        font=footer_font,
        fill=(foreground[0], foreground[1], foreground[2], 180),
    )

    return canvas


def save_asset(image: Image.Image, asset_id: str, out_dir: Path) -> Path:
    _, _, image_format = ASSETS[asset_id]
    if image_format == "JPEG":
        destination = out_dir / f"{asset_id}.jpg"
        image.convert("RGB").save(destination, "JPEG", quality=88, optimize=True, progressive=True)
        if destination.stat().st_size >= 1_000_000:
            image.convert("RGB").save(destination, "JPEG", quality=78, optimize=True, progressive=True)
        if destination.stat().st_size >= 1_000_000:
            raise SystemExit(f"{destination} exceeds GitHub's 1 MB social-preview limit")
    else:
        destination = out_dir / f"{asset_id}.png"
        image.save(destination, "PNG", optimize=True)
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--background", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--logo")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    background = Image.open(args.background)
    logo_path = Path(args.logo) if args.logo else None
    if logo_path and not logo_path.exists():
        raise SystemExit(f"Logo not found: {logo_path}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for asset_id in ASSETS:
        image = render_asset(asset_id, background, manifest, logo_path)
        destination = save_asset(image, asset_id, out_dir)
        print(f"Wrote {destination.resolve()} ({image.width}x{image.height})")


if __name__ == "__main__":
    main()
