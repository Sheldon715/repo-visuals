---
name: repo-visuals
description: Turn an open-source repository into a reusable launch identity by proposing distinct art directions, locking an approved visual system, and exporting coordinated repository and social assets. Use when a user asks for a README hero, GitHub social preview, release card, launch kit, repository branding, or consistent future release visuals. Do not use for general image generation, logo design, screenshots, or publishing repository settings.
---

# Repo Visuals

Create a project-aware visual identity that remains consistent across launch and future release assets.

## Workflow

1. Inspect only public-facing repository material: README, package metadata, approved logo, screenshots, and brand tokens. Run `scripts/inspect_repo.py <repo> --out <work-dir>/manifest.json` and correct any inferred copy or project type.
2. Never invent adoption claims, performance numbers, compatibility, customers, or release facts.
3. Run `scripts/plan_directions.py` to create three deliberately different directions. Read [references/visual-workflow.md](references/visual-workflow.md) before generating them.
4. Use the environment's image-generation capability once per direction. In Codex, use `$imagegen` and its built-in tool. Generate artwork only: no readable text, letters, logos, UI screenshots, badges, or watermarks.
5. Create one GitHub-social preview per direction with `lock_direction.py` and `compose_visual.py --asset github-social`, then build a comparison with `build_direction_board.py`.
6. Ask the user to choose a direction unless they explicitly delegated selection. Evaluate distinctiveness, repository fit, crop survival, and copy contrast rather than generic polish alone.
7. Lock the approved direction in `visual-lock.json`. This file is authoritative for future release assets; preserve it unless the user requests a redesign.
8. Render the full six-asset kit with `compose_visual.py --lock ...`, build the contact sheet, and verify exact copy, release, contrast, cropping, dimensions, and social-preview file size.
9. Fix copy, color, or spacing deterministically. Regenerate artwork only for a genuine art-direction or crop failure.

Use `output/repo-visuals/` in the target repository unless the user names another destination. Never overwrite existing launch assets without explicit permission; use a new output directory or versioned filenames.

## Required outputs

- `readme-hero.png`
- `github-social.jpg`
- `release-card.png`
- `product-gallery.png`
- `launch-post.jpg`
- `community-square.png`
- `contact-sheet.png`
- `manifest.json`
- `directions.json`
- `visual-lock.json`

Report the final paths, the artwork prompt, and any fields that still need user confirmation. Do not upload, publish, change repository settings, commit, or push unless the user separately authorizes that action.
