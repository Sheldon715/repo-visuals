#!/usr/bin/env python3
"""Resize an approved full-canvas ImageGen result without adding or altering design."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--width", required=True, type=int)
    parser.add_argument("--height", required=True, type=int)
    parser.add_argument("--format", choices=("PNG", "JPEG"), required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    source = Image.open(args.input).convert("RGB")
    source_ratio = source.width / source.height
    target_ratio = args.width / args.height
    ratio_error = abs(source_ratio - target_ratio) / target_ratio
    if ratio_error > 0.04:
        raise SystemExit(
            f"Aspect ratio differs by {ratio_error:.1%}; regenerate for the target shape "
            "instead of cropping away the authored composition."
        )

    result = ImageOps.fit(
        source,
        (args.width, args.height),
        Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "JPEG":
        result.save(destination, "JPEG", quality=90, optimize=True, progressive=True)
    else:
        result.save(destination, "PNG", optimize=True)
    print(f"Wrote {destination.resolve()} ({args.width}x{args.height})")


if __name__ == "__main__":
    main()
