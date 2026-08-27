# Full-canvas visual workflow

Read this reference before generating directions or adapting a selected identity.

## Direction generation

Run `inspect_repo.py`, then `plan_directions.py`. A direction prompt is a compact design brief with:

- a product-specific visual metaphor;
- a composition sketch covering grid, type zone, visual zone, and hierarchy;
- exact project copy;
- typographic behavior;
- palette, material language, and exclusions.

Generate the complete poster with ImageGen. Do not remove the text instruction or replace the composition sketch with “leave negative space for copy.”

## Review gate

Inspect every candidate at full size and as a thumbnail. Accept only when:

- project name and tagline are exact;
- no extra readable words or invented claims appear;
- typography participates in the visual metaphor;
- the canvas has a recognizable silhouette;
- the result does not resemble generic centered SaaS artwork;
- important content stays clear of the outer five percent.

For one localized defect, edit or retry while preserving all accepted details. Stop after two failed targeted attempts and expose the copy uncertainty instead of silently switching workflows.

## Lock and adapt

```bash
python scripts/lock_direction.py \
  --manifest <work-dir>/manifest.json \
  --directions <work-dir>/directions.json \
  --select <direction-id> \
  --artwork <work-dir>/<direction-id>/complete-poster.png \
  --out <work-dir>/visual-lock.json

python scripts/plan_assets.py \
  --lock <work-dir>/visual-lock.json \
  --out <work-dir>/asset-prompts.json
```

Use the locked artwork as an ImageGen reference for every new aspect ratio. Preserve visual identity, but redesign the whole layout for the target shape. A portrait asset should not be a crop of the wide poster.

## Export

When ImageGen returns the correct composition at a near-matching ratio, resize without adding design elements:

```bash
python scripts/export_generated.py \
  --input <approved-image> \
  --width 1280 --height 640 --format JPEG \
  --out <work-dir>/github-social.jpg
```

The exporter rejects ratio mismatches above four percent. Regenerate for the intended shape rather than cutting away the authored composition.

The older `compose_visual.py` remains an opt-in exact-copy fallback. Do not use it by default.
