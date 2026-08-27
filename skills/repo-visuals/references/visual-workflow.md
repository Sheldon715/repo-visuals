# Visual workflow

Read this reference before generating the master artwork.

## 1. Build the manifest

Run:

```bash
python scripts/inspect_repo.py <repo-path> --out <work-dir>/manifest.json
```

Prefer the user's explicit copy and brand choices over inferred values. Treat detected metadata as a draft.

## 2. Generate one master background

Use the manifest's `image_prompt` as the base. Normalize it into the image tool's preferred prompt format without adding products, people, logos, claims, or narrative elements not implied by the repository.

The composition must work across crops from `2:1` to `16:9`:

- quiet, dark negative space on the left;
- visual focus on the right-center;
- detail kept away from edges;
- no text of any kind;
- no baked-in title or logo.

Generate one background first. Create a second only if the first cannot survive the required crops or clearly conflicts with the repository.

## 3. Compose exact assets

Run:

```bash
python scripts/compose_visual.py --manifest <manifest> --background <image> --out-dir <work-dir>
```

Pass `--logo <path>` only when the repository already contains a user-approved raster logo. Do not fabricate a logo for this workflow.

## 4. Review together

Run:

```bash
python scripts/build_contact_sheet.py --input-dir <work-dir> --out <work-dir>/contact-sheet.png
```

Inspect the contact sheet at readable resolution. Check:

- exact spelling and release value;
- consistent art direction across all crops;
- legible title and tagline;
- no clipped logo or copy;
- no accidental generated lettering;
- correct dimensions and formats;
- social preview below 1 MB.

Regenerate the background only for artwork or crop failures. Change the manifest or compositor inputs for copy, color, spacing, and release corrections.
