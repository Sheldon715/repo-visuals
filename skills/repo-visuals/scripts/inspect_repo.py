#!/usr/bin/env python3
"""Inspect public repository metadata and create a repo-visuals manifest."""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any


SKIP_DIRS = {
    ".git",
    ".idea",
    ".next",
    ".venv",
    ".vscode",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "output",
    "target",
    "vendor",
}

EXTENSION_NAMES = {
    ".astro": "Astro",
    ".css": "CSS",
    ".dart": "Dart",
    ".go": "Go",
    ".html": "HTML",
    ".java": "Java",
    ".js": "JavaScript",
    ".jsx": "React",
    ".kt": "Kotlin",
    ".php": "PHP",
    ".py": "Python",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".swift": "Swift",
    ".ts": "TypeScript",
    ".tsx": "React + TypeScript",
    ".vue": "Vue",
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def load_package_json(repo: Path) -> dict[str, Any]:
    path = repo / "package.json"
    if not path.exists():
        return {}
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError:
        return {}


def load_pyproject(repo: Path) -> dict[str, Any]:
    path = repo / "pyproject.toml"
    if not path.exists():
        return {}
    try:
        return tomllib.loads(read_text(path)).get("project", {})
    except (tomllib.TOMLDecodeError, OSError):
        return {}


def find_readme(repo: Path) -> Path | None:
    for name in ("README.md", "README.rst", "README.txt", "README"):
        candidate = repo / name
        if candidate.exists():
            return candidate
    return None


def extract_readme_copy(text: str) -> tuple[str | None, str | None]:
    heading = None
    paragraphs: list[str] = []
    current: list[str] = []
    fenced = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if heading is None and line.startswith("# "):
            heading = re.sub(r"[\[\]`*_]", "", line[2:]).strip()
            continue
        if not line:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        if (
            line.startswith(("#", "!", "<", "[!", "|", "- ", "* ", ">"))
            or "shields.io" in line
        ):
            continue
        current.append(re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", line))

    if current:
        paragraphs.append(" ".join(current))

    description = next((p for p in paragraphs if 24 <= len(p) <= 320), None)
    return heading, description


def detect_stack(repo: Path) -> list[str]:
    counts: Counter[str] = Counter()
    for path in repo.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        name = EXTENSION_NAMES.get(path.suffix.lower())
        if name:
            counts[name] += 1
    return [name for name, _ in counts.most_common(4)]


def clean_name(value: str) -> str:
    cleaned = value.strip().removeprefix("@").replace("_", " ")
    if "/" in cleaned:
        cleaned = cleaned.rsplit("/", 1)[-1]
    return cleaned


def clamp_tagline(value: str, limit: int = 150) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) <= limit:
        return value
    shortened = value[: limit - 1].rsplit(" ", 1)[0]
    return f"{shortened}…"


def build_manifest(args: argparse.Namespace) -> dict[str, Any]:
    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        raise SystemExit(f"Repository directory not found: {repo}")

    package = load_package_json(repo)
    pyproject = load_pyproject(repo)
    readme_path = find_readme(repo)
    readme_heading, readme_description = extract_readme_copy(
        read_text(readme_path) if readme_path else ""
    )

    detected_name = (
        package.get("displayName")
        or package.get("name")
        or pyproject.get("name")
        or readme_heading
        or repo.name
    )
    detected_description = (
        package.get("description")
        or pyproject.get("description")
        or readme_description
        or "A focused open-source project built for developers."
    )
    detected_version = package.get("version") or pyproject.get("version") or "0.1.0"

    name = clean_name(args.name or str(detected_name))
    tagline = clamp_tagline(args.tagline or str(detected_description))
    version = str(args.release or detected_version).removeprefix("v")
    stack = detect_stack(repo)

    return {
        "schema_version": 1,
        "project": {
            "name": name,
            "tagline": tagline,
            "release": version,
            "repository_url": args.repository_url or "",
            "tech_stack": stack,
            "source_path": repo.name,
        },
        "brand": {
            "primary": args.primary,
            "secondary": args.secondary,
            "background": args.background,
            "foreground": args.foreground,
            "direction": args.direction,
        },
        "copy": {
            "eyebrow": args.eyebrow,
            "title": name,
            "subtitle": tagline,
            "release_label": f"RELEASE v{version}",
        },
        "assets": [
            {"id": "readme-hero", "width": 1600, "height": 900, "format": "PNG"},
            {"id": "github-social", "width": 1280, "height": 640, "format": "JPEG"},
            {"id": "release-card", "width": 1200, "height": 675, "format": "PNG"},
        ],
        "image_prompt": {
            "use_case": "ads-marketing",
            "asset_type": "text-free master artwork for open-source repository launch assets",
            "primary_request": (
                f"Create a polished abstract visual system for {name}, "
                f"an open-source project described as: {tagline}"
            ),
            "style": args.direction,
            "composition": (
                "Wide adaptable composition; quiet dark negative space on the left; "
                "visual focus on the right-center; important detail away from all edges"
            ),
            "palette": f"{args.background}, {args.primary}, {args.secondary}",
            "constraints": (
                "No text, letters, numbers, logos, badges, watermarks, screenshots, "
                "user interfaces, people, or third-party marks"
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--out", required=True, help="Manifest JSON output path")
    parser.add_argument("--name")
    parser.add_argument("--tagline")
    parser.add_argument("--release")
    parser.add_argument("--repository-url")
    parser.add_argument("--primary", default="#8B5CF6")
    parser.add_argument("--secondary", default="#22D3EE")
    parser.add_argument("--background", default="#09090B")
    parser.add_argument("--foreground", default="#F8FAFC")
    parser.add_argument("--eyebrow", default="OPEN SOURCE · VISUAL LAUNCH KIT")
    parser.add_argument(
        "--direction",
        default="editorial technology artwork with luminous depth and restrained detail",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = build_manifest(args)
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {destination.resolve()}")


if __name__ == "__main__":
    main()
