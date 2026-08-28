#!/usr/bin/env python3
"""Build a compact, shareable workflow GIF from the checked-in demo assets."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


WIDTH, HEIGHT = 960, 540
ACCENT = "#B7FF4A"
MINT = "#D8FBE6"
MUTED = "#8CA396"
INK = "#050806"
PANEL = "#0B120E"


def font(size: int, *, bold: bool = False, mono: bool = False) -> ImageFont.ImageFont:
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


def fit(path: Path, size: tuple[int, int], *, cover: bool = False) -> Image.Image:
    image = Image.open(path).convert("RGB")
    if cover:
        return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)
    return ImageOps.contain(image, size, method=Image.Resampling.LANCZOS)


def chrome(eyebrow: str, title: str, subtitle: str, step: str) -> Image.Image:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), INK)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, WIDTH, 8), fill=ACCENT)
    draw.text((48, 38), eyebrow.upper(), font=font(15, bold=True, mono=True), fill=ACCENT)
    draw.text((48, 67), title, font=font(30, bold=True), fill=MINT)
    draw.text((48, 109), subtitle, font=font(17), fill=MUTED)
    draw.text((862, 44), step, font=font(15, bold=True, mono=True), fill=MUTED)
    return canvas


def intro() -> Image.Image:
    canvas = chrome(
        "repo-visuals / pulsecheck",
        "Turn repository context into a launch identity.",
        "A Codex Skill that lets ImageGen own the complete canvas.",
        "01 / 06",
    )
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((48, 182, 912, 450), radius=18, fill=PANEL, outline="#1E3325", width=2)
    draw.text((86, 226), "README  →  direction sketches  →  ImageGen", font=font(29, bold=True), fill=MINT)
    draw.text((86, 291), "No ordinary text pasted over a background.", font=font(21), fill=ACCENT)
    draw.text((86, 350), "The title, signal, material, and hierarchy are authored together.", font=font(18), fill=MUTED)
    draw.line((86, 396, 868, 396), fill="#2C4A33", width=2)
    draw.text((86, 414), "github.com/Sheldon715/repo-visuals", font=font(17, mono=True), fill=MUTED)
    return canvas


def visual_slide(
    path: Path,
    eyebrow: str,
    title: str,
    subtitle: str,
    step: str,
    *,
    cover: bool = False,
) -> Image.Image:
    canvas = chrome(eyebrow, title, subtitle, step)
    draw = ImageDraw.Draw(canvas)
    frame = (48, 154, 912, 500)
    draw.rounded_rectangle(frame, radius=14, fill=PANEL, outline="#1E3325", width=2)
    visual = fit(path, (frame[2] - frame[0] - 12, frame[3] - frame[1] - 12), cover=cover)
    x = frame[0] + (frame[2] - frame[0] - visual.width) // 2
    y = frame[1] + (frame[3] - frame[1] - visual.height) // 2
    canvas.paste(visual, (x, y))
    return canvas


def outro() -> Image.Image:
    canvas = chrome(
        "try it on your next repository",
        "One command to install.",
        "Then ask your agent for three complete launch directions.",
        "06 / 06",
    )
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((48, 182, 912, 378), radius=18, fill=PANEL, outline="#1E3325", width=2)
    draw.text((84, 220), "npx skills add Sheldon715/repo-visuals@repo-visuals", font=font(22, mono=True), fill=ACCENT)
    draw.text((84, 282), "MIT licensed · Python 3.11+ · ImageGen-compatible", font=font(18), fill=MUTED)
    draw.text((84, 334), "github.com/Sheldon715/repo-visuals", font=font(17, mono=True), fill=MINT)
    return canvas


def fade_to_black(image: Image.Image, steps: int = 3) -> list[Image.Image]:
    black = Image.new("RGB", image.size, INK)
    return [Image.blend(image, black, index / steps) for index in range(1, steps + 1)]


def fade_from_black(image: Image.Image, steps: int = 3) -> list[Image.Image]:
    black = Image.new("RGB", image.size, INK)
    return [Image.blend(black, image, index / steps) for index in range(1, steps + 1)]


def zoom_slide(image: Image.Image, *, start: float, end: float, frames: int) -> list[Image.Image]:
    result: list[Image.Image] = []
    for index in range(frames):
        progress = index / max(frames - 1, 1)
        scale = start + (end - start) * progress
        crop_w = max(1, int(image.width / scale))
        crop_h = max(1, int(image.height / scale))
        left = (image.width - crop_w) // 2
        top = (image.height - crop_h) // 2
        crop = image.crop((left, top, left + crop_w, top + crop_h))
        result.append(crop.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS))
    return result


def build_frames(root: Path) -> tuple[list[Image.Image], list[int]]:
    intro_frame = intro()
    before = visual_slide(
        root / "before.png",
        "01 · inspect",
        "Start with the repository, not a blank prompt.",
        "Read the README, package metadata, and the product's real vocabulary.",
        "02 / 06",
    )
    directions = visual_slide(
        root / "direction-board.png",
        "02 · explore",
        "Generate three visual directions with different metaphors.",
        "Each sketch defines hierarchy, type behavior, and the visual system.",
        "03 / 06",
    )
    full_poster = Image.open(root / "v0.3" / "full-poster.png").convert("RGB")
    full_poster_slide = visual_slide(
        root / "v0.3" / "full-poster.png",
        "03 · generate",
        "ImageGen owns the complete composition.",
        "The title is part of the artwork—signals pass through the letterforms.",
        "04 / 06",
        cover=True,
    )
    comparison = visual_slide(
        root / "before-after.png",
        "04 · review",
        "Reject generic overlays and weak hierarchy.",
        "Keep the concept; repair only localized copy defects when needed.",
        "05 / 06",
        cover=True,
    )
    formats = visual_slide(
        root / "selected" / "contact-sheet.png",
        "05 · adapt",
        "Adapt the locked identity across six launch formats.",
        "README, social preview, release card, gallery, launch post, and square.",
        "06 / 06",
    )
    final = outro()

    slides = [intro_frame, before, directions, full_poster_slide, comparison, formats, final]
    frames: list[Image.Image] = []
    durations: list[int] = []
    for index, slide in enumerate(slides):
        hold = 5 if index in (0, 6) else 7
        frames.extend([slide] * hold)
        durations.extend([280] * hold)
        if index < len(slides) - 1:
            next_slide = slides[index + 1]
            frames.extend(fade_to_black(slide))
            frames.extend(fade_from_black(next_slide))
            durations.extend([70] * 6)

    # Use a short, gentle zoom on the hero to make the GIF feel authored rather than static.
    hero_start = (5 + 6) + (7 + 6) + (7 + 6)
    hero_end = hero_start + 7
    zoomed = zoom_slide(full_poster, start=1.0, end=1.07, frames=7)
    for index, frame in enumerate(zoomed):
        frames[hero_start + index] = frame
        durations[hero_start + index] = 280
    # Keep the transition into the hero visually consistent with the slide chrome.
    frames[hero_start - 1] = Image.blend(frames[hero_start - 1], full_poster_slide, 0.55)
    frames[hero_end] = Image.blend(full_poster_slide, frames[hero_end], 0.45)
    return frames, durations


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).parent)
    parser.add_argument("--out", type=Path, default=Path(__file__).parent / "v0.3" / "demo.gif")
    args = parser.parse_args()
    frames, durations = build_frames(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    palette_frames = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=96) for frame in frames]
    palette_frames[0].save(
        args.out,
        save_all=True,
        append_images=palette_frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )
    total_ms = sum(durations)
    print(f"Wrote {args.out.resolve()} ({len(frames)} frames, {total_ms / 1000:.1f}s)")


if __name__ == "__main__":
    main()
