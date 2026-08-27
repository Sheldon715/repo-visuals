# Visual workflow

Read this reference before generating directions or selecting the final identity.

## 1. Build the manifest

```bash
python scripts/inspect_repo.py <repo-path> --out <work-dir>/manifest.json
```

Treat detected metadata and project type as a draft. Prefer explicit user choices and repository evidence.

## 2. Plan three directions

```bash
python scripts/plan_directions.py \
  --manifest <work-dir>/manifest.json \
  --out <work-dir>/directions.json
```

The three directions must differ in visual metaphor, palette, material, energy, and composition—not merely color. Preserve the generated direction ids so later commands remain reproducible.

## 3. Generate and preview each direction

Generate one text-free background per direction with the direction's prompt. The artwork must keep copy-safe space on the left for wide crops and in the lower third for square or portrait crops.

For each direction:

```bash
python scripts/lock_direction.py \
  --manifest <work-dir>/manifest.json \
  --directions <work-dir>/directions.json \
  --select <direction-id> \
  --background <work-dir>/<direction-id>/background.png \
  --out <work-dir>/<direction-id>/visual-lock.json

python scripts/compose_visual.py \
  --lock <work-dir>/<direction-id>/visual-lock.json \
  --background <work-dir>/<direction-id>/background.png \
  --out-dir <work-dir>/<direction-id> \
  --asset github-social
```

Build the comparison board:

```bash
python scripts/build_direction_board.py \
  --directions <work-dir>/directions.json \
  --previews-dir <work-dir> \
  --out <work-dir>/direction-board.png
```

## 4. Select and lock

Prefer the direction that:

- expresses the repository's product type instead of generic AI imagery;
- remains recognizable as a small thumbnail;
- supports every required crop;
- makes real copy legible without covering the main artwork;
- can plausibly support future release cards.

Copy the selected lock and background into the final output directory as `visual-lock.json` and `master-background.png`. Do not merge details from multiple directions unless the user requests a new iteration.

## 5. Render and review the complete kit

```bash
python scripts/compose_visual.py \
  --lock <work-dir>/visual-lock.json \
  --background <work-dir>/master-background.png \
  --out-dir <work-dir>

python scripts/build_contact_sheet.py \
  --input-dir <work-dir> \
  --out <work-dir>/contact-sheet.png
```

Inspect the contact sheet at readable resolution. Verify exact spelling, release value, crop survival, title contrast, file formats, dimensions, and the GitHub social preview's 1 MB limit.

Use the existing `visual-lock.json` for later releases. Update only release copy unless the user asks to redesign the identity.
