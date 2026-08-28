# First-wave launch drafts

These are platform-specific drafts for review before publishing. They intentionally
ask for critique and usage feedback instead of asking for coordinated upvotes.

Repository: <https://github.com/Sheldon715/repo-visuals>

## DEV / #showdev

### Title

I stopped overlaying text on AI images—how I made ImageGen own the whole launch canvas

### Body

Most repository launch graphics follow the same recipe: generate a background, then
place ordinary text on top. The result is usable, but it still looks like a template.

I built `repo-visuals`, a Codex Skill that treats the entire image as the design:

- reads a repository README and extracts the product story;
- proposes three visual directions before generation;
- lets ImageGen generate the artwork *and* typography as one composition;
- checks copy, hierarchy, contrast, and legibility before exporting six launch-ready
  formats.

The skill is deliberately small: the agent owns the reasoning and prompt iteration,
while Python/Pillow only handles deterministic contact sheets and export checks.

The README includes a 15-second workflow demo and the full-canvas before/after:

<https://github.com/Sheldon715/repo-visuals>

If you build agent skills or developer tools, I would love feedback on the workflow:
which part would you make more deterministic, and which launch format would you add?

## Reddit / r/AIDevsBuilders

### Title

I built a Codex skill that turns a README into a complete launch visual

### Body

I kept seeing the same problem in AI-generated repo graphics: the image is interesting,
but the title and product message are pasted on afterward, so the result feels generic.

`repo-visuals` is my attempt at a different workflow. It reads a README, proposes three
art directions, asks ImageGen to generate the whole canvas (including display typography),
then runs copy/contrast/legibility checks and exports six aspect-specific assets.

Built with Codex + ImageGen, with Python/Pillow used only for deterministic review sheets
and export checks. The hardest part was keeping the generated typography readable without
falling back to a normal text-overlay pipeline.

Demo and source: <https://github.com/Sheldon715/repo-visuals>

What would you test first: the direction-planning step, the full-canvas prompt, or the
copy QA loop?

## OpenAI Developer Community / Codex

### Title

What should a Codex Skill own vs. ImageGen? I tested a full-canvas workflow

### Body

I am experimenting with a boundary between agent reasoning and image generation for
developer-facing launch assets.

In [`repo-visuals`](https://github.com/Sheldon715/repo-visuals), the Codex Skill owns
README extraction, audience/message decisions, direction planning, retries, and QA.
ImageGen owns the visual composition—including the display typography—rather than
receiving a finished background that later gets covered by HTML/Pillow text. Pillow is
kept for deterministic contact sheets and export checks only.

The current workflow produces six aspect-specific outputs and includes a short demo in
the README. I am especially interested in feedback on three questions:

1. Should copy QA be a hard gate or a warning when generated lettering is uncertain?
2. Which metadata would make a generated launch asset reproducible across model versions?
3. What should a reusable Codex Skill expose as inputs: audience, tone, brand constraints,
   or all of the above?

Source and demo: <https://github.com/Sheldon715/repo-visuals>

