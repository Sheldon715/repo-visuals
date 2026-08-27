---
name: repo-visuals
description: Create a coordinated visual launch kit for an open-source repository using AI-generated, text-free artwork plus deterministic typography. Use when a user asks for a README hero, GitHub social preview, release announcement card, repository banner, or matching launch images. Do not use for general image generation, logo design, screenshots, or publishing repository settings.
---

# Repo Visuals

Create one coherent visual direction and export exact, usable repository launch assets.

## Workflow

1. Inspect the target repository's public-facing material: README, package metadata, existing logo, screenshots, and brand tokens. Do not send source files to an image service.
2. Run `scripts/inspect_repo.py <repo> --out <work-dir>/manifest.json`. Override the detected name, tagline, release, colors, or repository URL when the user supplied better values.
3. Review the manifest. Never invent adoption claims, performance numbers, compatibility, customers, or release facts.
4. Read [references/visual-workflow.md](references/visual-workflow.md) before generating artwork. Read [references/asset-specs.md](references/asset-specs.md) when changing sizes, safe areas, copy, or formats.
5. Use the environment's image-generation capability to create one master raster background. In Codex, use the installed `$imagegen` workflow and its built-in tool. Generate artwork only: no readable text, letters, logos, UI screenshots, badges, or watermarks.
6. Save the selected background in the work directory, then run `scripts/compose_visual.py` with the manifest and background.
7. Run `scripts/build_contact_sheet.py`, inspect the contact sheet, and verify the title, tagline, release, contrast, cropping, dimensions, and GitHub social-preview file size.
8. Make only the targeted correction needed. Do not regenerate artwork merely to fix typography or dimensions; fix those deterministically.

Use `output/repo-visuals/` in the target repository unless the user names another destination. Never overwrite existing launch assets without explicit permission; use a new output directory or versioned filenames.

## Required outputs

- `readme-hero.png`
- `github-social.jpg`
- `release-card.png`
- `contact-sheet.png`
- `manifest.json`

Report the final paths, the artwork prompt, and any fields that still need user confirmation. Do not upload, publish, change repository settings, commit, or push unless the user separately authorizes that action.
