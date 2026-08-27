#!/usr/bin/env python3
"""Lock one approved direction into a reusable visual identity file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--directions", required=True)
    parser.add_argument("--select", required=True, help="Direction id")
    artwork = parser.add_mutually_exclusive_group(required=True)
    artwork.add_argument("--artwork", help="Approved complete direction artwork")
    artwork.add_argument("--background", help="Legacy V0.2 background artwork")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    direction_set = json.loads(Path(args.directions).read_text(encoding="utf-8"))
    selected = next(
        (item for item in direction_set["directions"] if item["id"] == args.select),
        None,
    )
    if selected is None:
        choices = ", ".join(item["id"] for item in direction_set["directions"])
        raise SystemExit(f"Unknown direction {args.select!r}. Choose one of: {choices}")

    artwork_path = Path(args.artwork or args.background)
    payload = {
        "schema_version": 2,
        "selected_direction": {
            "id": selected["id"],
            "name": selected["name"],
            "rationale": selected["rationale"],
            "style": selected["style"],
            "sketch": selected["sketch"],
        },
        "project": manifest["project"],
        "copy": manifest["copy"],
        "brand": selected["brand"],
        "layout": selected["layout"],
        "assets": manifest["assets"],
        "artwork": {
            "reference": artwork_path.name,
            "mode": "full-canvas" if args.artwork else "legacy-compositor",
            "prompt": selected["prompt"],
        },
    }
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Locked {selected['name']} -> {destination.resolve()}")


if __name__ == "__main__":
    main()
