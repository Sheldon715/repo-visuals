#!/usr/bin/env python3
"""Build full-canvas ImageGen prompts for every asset in a locked identity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ASSET_RECIPES: dict[str, str] = {
    "readme-hero": "cinematic 16:9 repository hero; immediate product recognition at README width",
    "github-social": "bold 2:1 social preview; readable and distinctive as a small link thumbnail",
    "release-card": "editorial 16:9 release announcement; release marker woven into the composition",
    "product-gallery": "polished wide gallery image; communicates the product metaphor at a glance",
    "launch-post": "vertical 4:5 campaign poster; strong top-to-bottom rhythm and mobile readability",
    "community-square": "square community tile; compact hierarchy and unmistakable silhouette",
}


def prompt_for(lock: dict[str, Any], asset: dict[str, Any]) -> dict[str, Any]:
    direction = lock["selected_direction"]
    project = lock["project"]
    copy = lock["copy"]
    brand = lock["brand"]
    asset_id = asset["id"]
    eyebrow = copy["release_label"] if asset_id in {"release-card", "launch-post"} else ""
    exact_lines = [copy["title"], copy["subtitle"]]
    if eyebrow:
        exact_lines.insert(0, eyebrow)
    quoted = ", ".join(f'"{line}"' for line in exact_lines)
    sketch = direction.get("sketch", {})
    return {
        "use_case": "ads-marketing",
        "asset_type": ASSET_RECIPES[asset_id],
        "primary_request": (
            f"Create the complete {asset_id} for {project['name']} in the approved "
            f"{direction['name']} identity. Generate the entire finished design, including "
            "art direction, integrated typography, layout, texture, and final polish."
        ),
        "reference_image": (
            f"Use {lock['artwork']['reference']} as the identity reference. Preserve its visual "
            "metaphor, material language, palette, and typographic personality; redesign the "
            "composition for this aspect ratio instead of merely cropping it."
        ),
        "sketch": {
            "grid": sketch.get("grid", "asymmetric editorial grid"),
            "type_zone": sketch.get("type_zone", "typography integrated with the subject"),
            "visual_zone": sketch.get("visual_zone", "dominant product metaphor"),
            "hierarchy": sketch.get("hierarchy", "dominant title and concise supporting copy"),
        },
        "palette": ", ".join(
            (brand["background"], brand["primary"], brand["secondary"], brand["foreground"])
        ),
        "text": (
            f"Render exactly these readable lines and no others: {quoted}. "
            "Spell and punctuate every character verbatim."
        ),
        "dimensions": {
            "width": asset["width"],
            "height": asset["height"],
            "format": asset["format"],
        },
        "constraints": (
            "Typography must feel authored as part of the artwork, not pasted into a box. "
            "No extra words, fake metrics, installation commands, UI screenshots, logos, badges, "
            "watermarks, third-party marks, generic purple gradients, or plain template overlays."
        ),
        "qa": [
            "exact text and punctuation",
            "title readable at thumbnail size",
            "typography visibly interacts with the visual concept",
            "no unsupported claims or extra readable text",
            "important content clear of the outer five percent",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    lock = json.loads(Path(args.lock).read_text(encoding="utf-8"))
    payload = {
        "schema_version": 1,
        "mode": "full-canvas-imagegen",
        "reference_artwork": lock["artwork"]["reference"],
        "assets": [
            {"id": asset["id"], "prompt": prompt_for(lock, asset)}
            for asset in lock["assets"]
        ],
    }
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {destination.resolve()}")


if __name__ == "__main__":
    main()
