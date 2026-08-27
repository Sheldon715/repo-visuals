# Asset specifications

Read this reference when changing output dimensions, formats, layout, copy, or export behavior.

## Default assets

| Asset | Dimensions | Format | Purpose |
| --- | ---: | --- | --- |
| README hero | 1600 x 900 | PNG | First visual in a repository README |
| GitHub social preview | 1280 x 640 | JPEG | Repository link previews on social platforms |
| Release card | 1200 x 675 | PNG | Release notes and announcement posts |
| Product gallery | 1270 x 760 | PNG | Product-directory and launch galleries |
| Launch post | 1200 x 1500 | JPEG | Portrait social announcement |
| Community square | 1080 x 1080 | PNG | Community, chat, and directory thumbnail |

GitHub recommends `1280 x 640` for best social-preview display and requires the upload to remain below 1 MB. The compositor saves this asset as an optimized JPEG and fails if it is still too large.

## Copy hierarchy

Use only values present in the manifest or explicitly provided by the user:

1. optional eyebrow or release label;
2. project name;
3. one concise tagline;
4. optional repository host/path.

Do not place feature lists, installation commands, badges, or paragraphs on these assets. Keep the title to two lines and the tagline to three lines. If copy does not fit, shorten it in the manifest instead of shrinking it into illegibility.

## Safe areas

- Keep essential copy at least 7% of canvas width from every edge.
- Reserve the left 56% for deterministic copy in wide assets.
- Reserve the lower 42% for deterministic copy in square and portrait assets.
- Keep high-detail generated artwork primarily on the right.
- Do not put essential artwork in the outer 5%; crops and embeds may hide it.
- Use a solid or strongly darkened text region. Do not rely on a busy generated texture for contrast.

## Background invariants

The generated master background must survive wide, square, and portrait crops. It must contain no readable text, characters resembling text, logos, watermarks, badges, interface screenshots, or fake product claims. It may contain abstract symbols only when they do not resemble a third-party mark.
