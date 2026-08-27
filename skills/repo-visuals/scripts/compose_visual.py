#!/usr/bin/env python3
"""Compose an exact six-asset launch kit over approved AI artwork."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ASSET_DEFAULTS: dict[str, tuple[int, int, str]] = {
    "readme-hero": (1600, 900, "PNG"),
    "github-social": (1280, 640, "JPEG"),
    "release-card": (1200, 675, "PNG"),
    "product-gallery": (1270, 760, "PNG"),
    "launch-post": (1200, 1500, "JPEG"),
    "community-square": (1080, 1080, "PNG"),
}


def parse_hex(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Expected a six-digit hex color, got: {value!r}")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def font_candidates(bold: bool) -> list[Path]:
    names = (
        ["segoeuib.ttf", "arialbd.ttf", "msyhbd.ttc", "DejaVuSans-Bold.ttf"]
        if bold
        else ["segoeui.ttf", "arial.ttf", "msyh.ttc", "DejaVuSans.ttf"]
    )
    roots = [
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts",
        Path("/usr/share/fonts/truetype/dejavu"),
        Path("/Library/Fonts"),
        Path.home() / "Library/Fonts",
    ]
    return [root / name for root in roots for name in names]


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    for candidate in font_candidates(bold):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default(size=size)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def split_tokens(text: str) -> tuple[list[str], str]:
    words = text.split()
    if len(words) == 1 and len(text) > 18:
        return list(text), ""
    return words, " "


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
    max_lines: int,
) -> list[str]:
    tokens, joiner = split_tokens(text.strip())
    if not tokens:
        return []
    lines: list[str] = []
    current = tokens.pop(0)
    while tokens:
        candidate = f"{current}{joiner}{tokens[0]}"
        if text_width(draw, candidate, font) <= max_width:
            current = candidate
            tokens.pop(0)
        else:
            lines.append(current)
            current = tokens.pop(0)
            if len(lines) == max_lines - 1:
                if tokens:
                    current = f"{current}{joiner}{joiner.join(tokens)}"
                    tokens = []
                break
    lines.append(current)
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
        if all(text_width(draw, line, font) <= max_width for line in lines):
            return font, lines
    font = load_font(min_size, bold=True)
    return font, wrap_text(draw, text, font, max_width, max_lines)


def add_contrast_overlay(
    image: Image.Image,
    placement: str,
    surface: str,
) -> Image.Image:
    width, height = image.size
    color = (248, 245, 235) if surface == "light" else (3, 5, 8)
    if placement == "left":
        values = [
            int(235 * max(0.0, 1.0 - (x / max(width - 1, 1)) / 0.78) ** 1.65)
            for x in range(width)
        ]
        mask = Image.new("L", (width, 1))
        mask.putdata(values)
        mask = mask.resize((width, height))
    else:
        values = [
            int(240 * max(0.0, ((y / max(height - 1, 1)) - 0.28) / 0.72) ** 1.45)
            for y in range(height)
        ]
        mask = Image.new("L", (1, height))
        mask.putdata(values)
        mask = mask.resize((width, height))
    overlay = Image.new("RGBA", image.size, (*color, 0))
    overlay.putalpha(mask)
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
    canvas.alpha_composite(logo, position)
    return logo.width + max(18, max_size // 5)


def asset_specs(config: dict[str, Any]) -> list[dict[str, Any]]:
    specs = []
    configured = {item["id"]: item for item in config.get("assets", [])}
    for asset_id, (width, height, image_format) in ASSET_DEFAULTS.items():
        item = configured.get(asset_id, {})
        specs.append(
            {
                "id": asset_id,
                "width": int(item.get("width", width)),
                "height": int(item.get("height", height)),
                "format": item.get("format", image_format),
            }
        )
    return specs


def draw_landscape_copy(
    canvas: Image.Image,
    config: dict[str, Any],
    asset_id: str,
    logo_path: Path | None,
) -> None:
    width, height = canvas.size
    draw = ImageDraw.Draw(canvas)
    brand = config["brand"]
    copy = config["copy"]
    foreground = parse_hex(brand["foreground"])
    primary = parse_hex(brand["primary"])
    secondary = parse_hex(brand["secondary"])
    margin_x = int(width * 0.072)
    margin_y = int(height * 0.105)
    max_width = int(width * 0.48)
    scale = width / 1600

    accent_width = max(5, int(8 * scale))
    draw.rounded_rectangle(
        (margin_x, margin_y, margin_x + accent_width, margin_y + int(height * 0.11)),
        radius=accent_width // 2,
        fill=primary,
    )
    direction = config.get("selected_direction", {}).get("name")
    if asset_id == "release-card":
        eyebrow = copy["release_label"]
    elif direction:
        eyebrow = f"OPEN SOURCE · {direction.upper()}"
    else:
        eyebrow = copy["eyebrow"]
    eyebrow_font = load_font(max(17, int(22 * scale)), bold=True)
    draw.text(
        (margin_x + accent_width + max(16, int(22 * scale)), margin_y + int(height * 0.018)),
        eyebrow,
        font=eyebrow_font,
        fill=secondary,
    )

    title_y = margin_y + int(height * 0.18)
    title_font, title_lines = fit_title_font(
        draw,
        copy["title"],
        max_width,
        2,
        start_size=max(54, int(94 * scale)),
        min_size=max(36, int(56 * scale)),
    )
    title_text = "\n".join(title_lines)
    spacing = max(5, int(8 * scale))
    title_box = draw.multiline_textbbox(
        (margin_x, title_y), title_text, font=title_font, spacing=spacing
    )
    draw.multiline_text(
        (margin_x, title_y), title_text, font=title_font, fill=foreground, spacing=spacing
    )

    subtitle_font = load_font(max(20, int(29 * scale)))
    subtitle_lines = wrap_text(draw, copy["subtitle"], subtitle_font, max_width, 3)
    draw.multiline_text(
        (margin_x, title_box[3] + int(height * 0.05)),
        "\n".join(subtitle_lines),
        font=subtitle_font,
        fill=(*foreground[:3], 210),
        spacing=max(7, int(11 * scale)),
    )

    footer_y = height - margin_y - max(42, int(56 * scale))
    logo_offset = draw_logo(
        canvas, logo_path, (margin_x, footer_y), max(38, int(52 * scale))
    )
    draw.text(
        (margin_x + logo_offset, footer_y + max(7, int(10 * scale))),
        footer_label(config),
        font=load_font(max(16, int(21 * scale)), bold=True),
        fill=(*foreground[:3], 185),
    )


def draw_stacked_copy(
    canvas: Image.Image,
    config: dict[str, Any],
    asset_id: str,
    logo_path: Path | None,
) -> None:
    width, height = canvas.size
    draw = ImageDraw.Draw(canvas)
    brand = config["brand"]
    copy = config["copy"]
    foreground = parse_hex(brand["foreground"])
    primary = parse_hex(brand["primary"])
    secondary = parse_hex(brand["secondary"])
    margin = int(width * 0.075)
    max_width = width - margin * 2
    start_y = int(height * (0.59 if height > width else 0.55))
    accent_width = max(5, int(width * 0.007))
    draw.rounded_rectangle(
        (margin, start_y, margin + accent_width, start_y + int(height * 0.065)),
        radius=accent_width // 2,
        fill=primary,
    )
    direction = config.get("selected_direction", {}).get("name", "LAUNCH IDENTITY")
    eyebrow = copy["release_label"] if asset_id == "launch-post" else direction.upper()
    draw.text(
        (margin + accent_width + 18, start_y + 7),
        eyebrow,
        font=load_font(max(18, int(width * 0.02)), bold=True),
        fill=secondary,
    )

    title_y = start_y + int(height * 0.09)
    title_font, title_lines = fit_title_font(
        draw,
        copy["title"],
        max_width,
        2,
        start_size=max(62, int(width * 0.085)),
        min_size=max(42, int(width * 0.055)),
    )
    title_text = "\n".join(title_lines)
    title_box = draw.multiline_textbbox(
        (margin, title_y), title_text, font=title_font, spacing=7
    )
    draw.multiline_text(
        (margin, title_y), title_text, font=title_font, fill=foreground, spacing=7
    )

    subtitle_font = load_font(max(22, int(width * 0.027)))
    subtitle_lines = wrap_text(draw, copy["subtitle"], subtitle_font, max_width, 3)
    draw.multiline_text(
        (margin, title_box[3] + int(height * 0.026)),
        "\n".join(subtitle_lines),
        font=subtitle_font,
        fill=(*foreground[:3], 215),
        spacing=10,
    )

    footer_y = height - int(height * 0.075)
    logo_size = max(40, int(width * 0.048))
    logo_offset = draw_logo(canvas, logo_path, (margin, footer_y - logo_size), logo_size)
    draw.text(
        (margin + logo_offset, footer_y - logo_size + 10),
        footer_label(config),
        font=load_font(max(17, int(width * 0.019)), bold=True),
        fill=(*foreground[:3], 185),
    )


def footer_label(config: dict[str, Any]) -> str:
    project = config["project"]
    repository_url = project.get("repository_url", "")
    if repository_url:
        return repository_url.removeprefix("https://").removeprefix("http://").rstrip("/")
    stack = project.get("tech_stack") or []
    return " · ".join(stack[:3]) or project.get("type", "OPEN SOURCE").upper()


def render_asset(
    spec: dict[str, Any],
    background: Image.Image,
    config: dict[str, Any],
    logo_path: Path | None,
) -> Image.Image:
    width, height = spec["width"], spec["height"]
    stacked = width / height < 1.4
    focal_x = float(config.get("layout", {}).get("focal_x", 0.65))
    centering = (focal_x if stacked else 0.5, 0.47 if stacked else 0.5)
    base = ImageOps.fit(
        background.convert("RGB"),
        (width, height),
        method=Image.Resampling.LANCZOS,
        centering=centering,
    ).filter(ImageFilter.GaussianBlur(radius=0.12))
    surface = config.get("layout", {}).get("surface", "dark")
    canvas = add_contrast_overlay(base, "bottom" if stacked else "left", surface)
    if stacked:
        draw_stacked_copy(canvas, config, spec["id"], logo_path)
    else:
        draw_landscape_copy(canvas, config, spec["id"], logo_path)
    return canvas


def save_asset(image: Image.Image, spec: dict[str, Any], out_dir: Path) -> Path:
    asset_id = spec["id"]
    image_format = spec["format"].upper()
    if image_format in {"JPEG", "JPG"}:
        destination = out_dir / f"{asset_id}.jpg"
        image.convert("RGB").save(destination, "JPEG", quality=88, optimize=True, progressive=True)
        if asset_id == "github-social" and destination.stat().st_size >= 1_000_000:
            image.convert("RGB").save(destination, "JPEG", quality=78, optimize=True, progressive=True)
        if asset_id == "github-social" and destination.stat().st_size >= 1_000_000:
            raise SystemExit(f"{destination} exceeds GitHub's 1 MB social-preview limit")
    else:
        destination = out_dir / f"{asset_id}.png"
        image.save(destination, "PNG", optimize=True)
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--lock", help="Approved visual-lock.json")
    source.add_argument("--manifest", help="Legacy manifest without direction locking")
    parser.add_argument("--background", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--logo")
    parser.add_argument(
        "--asset",
        action="append",
        choices=tuple(ASSET_DEFAULTS),
        help="Render only this asset id; repeat for multiple assets",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.lock or args.manifest)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    background = Image.open(args.background)
    logo_path = Path(args.logo) if args.logo else None
    if logo_path and not logo_path.exists():
        raise SystemExit(f"Logo not found: {logo_path}")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    specs = asset_specs(config)
    if args.asset:
        selected_assets = set(args.asset)
        specs = [spec for spec in specs if spec["id"] in selected_assets]
    for spec in specs:
        image = render_asset(spec, background, config, logo_path)
        destination = save_asset(image, spec, out_dir)
        print(f"Wrote {destination.resolve()} ({image.width}x{image.height})")


if __name__ == "__main__":
    main()
