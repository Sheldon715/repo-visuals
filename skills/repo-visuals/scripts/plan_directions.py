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
        "asset_type": "text-free master artwork for a coordinated open-source launch identity",
        "primary_request": (
            f"Create the {preset['name']} visual direction for {name}, a {project_type} "
            f"described as: {tagline}. Depict {preset['subject']}."
        ),
        "style": preset["style"],
        "composition": (
            "Adaptable composition for 2:1, 16:9, square, and 4:5 crops; quiet copy-safe "
            "space on the left in wide crops and in the lower third for square or portrait crops; "
            "main visual focus in the upper-right center; important detail away from all edges"
        ),
        "palette": ", ".join(
            (brand["background"], brand["primary"], brand["secondary"], brand["foreground"])
        ),
        "constraints": (
            "No text, letters, numbers, code, logos, badges, watermarks, screenshots, "
            "interface labels, people, or third-party marks"
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
