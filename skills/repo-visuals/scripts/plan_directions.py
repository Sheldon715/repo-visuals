#!/usr/bin/env python3
"""Create three distinct, project-aware visual directions from a manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DIRECTION_PRESETS: tuple[dict[str, Any], ...] = (
    {
        "id": "signal-terminal",
        "name": "Signal Terminal",
        "rationale": "Feels native to developer tools while turning status and command output into a recognizable visual language.",
        "brand": {
            "primary": "#B7FF5A",
            "secondary": "#80F5D2",
            "background": "#050806",
            "foreground": "#F4FFE8",
        },
        "layout": {"surface": "dark", "focal_x": 0.67, "density": "precise"},
        "sketch": {
            "grid": "asymmetric 5-column poster grid",
            "type_zone": "project name integrated into the left-center instrument panel",
            "visual_zone": "monitoring instrument occupies the right two-thirds",
            "hierarchy": "small category label, dominant product name, quiet one-line promise",
        },
        "style": "tactile terminal instrumentation, luminous signal traces, crisp technical editorial art",
        "subject": "a compact command-line monitoring instrument built from pulse traces, status nodes, and modular terminal-like planes",
    },
    {
        "id": "editorial-blueprint",
        "name": "Editorial Blueprint",
        "rationale": "Looks more like a designed open-source publication than an AI-tool cliché, with strong contrast and memorable print energy.",
        "brand": {
            "primary": "#1947E5",
            "secondary": "#F05237",
            "background": "#F1EBD8",
            "foreground": "#111318",
        },
        "layout": {"surface": "light", "focal_x": 0.66, "density": "editorial"},
        "sketch": {
            "grid": "Swiss 12-column editorial grid with deliberate overlaps",
            "type_zone": "large product name crosses the grid and interacts with routing lines",
            "visual_zone": "diagram modules build a diagonal path from lower-left to upper-right",
            "hierarchy": "oversized title, compact subtitle, tiny publication metadata",
        },
        "style": "Swiss editorial poster, blueprint geometry, screen-print texture, confident asymmetric composition",
        "subject": "an abstract open-source system diagram made from bold status circles, routing lines, modular cards, and measured grid marks",
    },
    {
        "id": "kinetic-pulse",
        "name": "Kinetic Pulse",
        "rationale": "Creates launch-day energy and strong thumbnail recognition without falling back to generic purple glass objects.",
        "brand": {
            "primary": "#FF5A54",
            "secondary": "#FFD166",
            "background": "#140807",
            "foreground": "#FFF5E8",
        },
        "layout": {"surface": "dark", "focal_x": 0.68, "density": "bold"},
        "sketch": {
            "grid": "radial poster system with an offset typographic anchor",
            "type_zone": "product name cuts through the pulse field as part of the composition",
            "visual_zone": "concentric uptime pulse dominates the center-right",
            "hierarchy": "bold title, short promise, one restrained release marker",
        },
        "style": "bold kinetic graphic design, layered paper depth, radiant pulse rings, sharp contemporary poster art",
        "subject": "a dynamic uptime pulse moving through a network of endpoints, with bold concentric waves and clear status transitions",
    },
)


def build_prompt(project: dict[str, Any], preset: dict[str, Any]) -> dict[str, str]:
    name = project["name"]
    tagline = project["tagline"].rstrip(".")
    project_type = project.get("type", "developer-tool")
    brand = preset["brand"]
    return {
        "use_case": "ads-marketing",
        "asset_type": "complete 2:1 open-source launch poster including integrated typography",
        "primary_request": (
            f"Create the {preset['name']} visual direction for {name}, a {project_type} "
            f"described as: {tagline}. Depict {preset['subject']}."
        ),
        "style": preset["style"],
        "composition": (
            f"{preset['sketch']['grid']}; {preset['sketch']['type_zone']}; "
            f"{preset['sketch']['visual_zone']}; {preset['sketch']['hierarchy']}. "
            "Treat typography, shapes, texture, and subject as one authored composition—not "
            "artwork with a text box placed on top."
        ),
        "palette": ", ".join(
            (brand["background"], brand["primary"], brand["secondary"], brand["foreground"])
        ),
        "text": (
            f'Render exactly these two lines and no other readable copy: "{name}" and '
            f'"{project["tagline"]}" Spell every character verbatim.'
        ),
        "typography": (
            "Custom display typography that belongs to the visual concept; strong hierarchy, "
            "editorial spacing, crisp readable letterforms, no generic centered SaaS banner"
        ),
        "constraints": (
            "No extra words, fake interface labels, code, logos, badges, watermarks, people, "
            "third-party marks, generic gradient blobs, or text floating inside a plain overlay panel"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    project = manifest["project"]
    directions = []
    for preset in DIRECTION_PRESETS:
        direction = {key: value for key, value in preset.items() if key not in {"subject"}}
        direction["prompt"] = build_prompt(project, preset)
        directions.append(direction)

    payload = {
        "schema_version": 1,
        "project": {
            "name": project["name"],
            "type": project.get("type", "developer-tool"),
        },
        "directions": directions,
    }
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {destination.resolve()}")


if __name__ == "__main__":
    main()
