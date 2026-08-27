---
name: repo-visuals
description: Turn an open-source repository into an art-directed launch identity by generating complete ImageGen compositions with integrated typography, then adapting the approved identity across repository and social assets. Use for README heroes, GitHub social previews, release cards, launch kits, repository branding, or consistent future release visuals. Do not use for general image generation, logo design, screenshots, or publishing repository settings.
---

# Repo Visuals

Create complete, desirable launch visuals—not generated backgrounds with template text placed over them.

## Creative rule

Use ImageGen for the entire authored canvas: composition, typography, product metaphor, texture, lighting, and hierarchy. The title must visibly interact with the visual system. Do not reserve a blank rectangle for a local compositor.

Local scripts may inspect repository metadata, plan prompts, compare outputs, verify copy and dimensions, and resize an already approved canvas. They must not add ordinary title/tagline overlays in the default workflow.

## Workflow

1. Inspect only public-facing repository material with `scripts/inspect_repo.py <repo> --out <work-dir>/manifest.json`. Correct inferred copy or project type. Never invent claims, metrics, customers, compatibility, or release facts.
2. Read [references/visual-workflow.md](references/visual-workflow.md), then run `scripts/plan_directions.py`. Each direction must specify a different metaphor, composition sketch, typographic behavior, palette, and material language.
3. Use `$imagegen` once per direction to generate a complete direction poster with the exact project name and tagline. Pass the generated prompt including `text`, `typography`, and `sketch`; do not rewrite it as a background prompt.
4. Inspect each image at readable resolution. Reject any candidate with misspelled text, extra readable words, generic text-box composition, unsupported claims, weak thumbnail hierarchy, or obvious crop failure.
5. Ask the user to choose unless selection was delegated. Lock the approved complete artwork with `lock_direction.py --artwork ...`.
6. Run `plan_assets.py` to create aspect-specific full-canvas prompts. For each asset, give ImageGen the approved artwork as an identity reference and ask it to redesign the whole composition for the new aspect ratio; do not simply crop one master across every shape.
7. Permit at most two targeted attempts for copy or layout defects per asset. Each retry should name one defect and preserve everything else. If exact text still fails, report it; use the legacy compositor only when the user explicitly prioritizes exact copy over fully integrated art direction.
8. Use `export_generated.py` only to resize an approved result whose aspect ratio already matches within 4%. Build the contact sheet and visually inspect every final asset.

Use `output/repo-visuals/` unless the user names another destination. Never overwrite existing assets without permission; use a new versioned directory.

## Required outputs

- complete generated image for every requested asset
- `manifest.json`
- `directions.json`
- `visual-lock.json`
- `asset-prompts.json`
- `contact-sheet.png` when generating multiple assets

Report final paths, the full prompt set, built-in or fallback ImageGen mode, and any unresolved copy uncertainty. Do not upload, publish, change repository settings, commit, or push unless separately authorized.
