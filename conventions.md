# Conventions

Durable rules distilled from the changelog — forward-propagating: once a
convention lands here, all future lectures follow it (earlier ones are
retrofitted only by explicit decision). Seeded from the donor project
(PHYS 567); grows as the course proceeds.

## Authoring (engine-neutral content subset)
- Frames, blocks, columns, overlay specs, and course macros only — no
  target-specific code in lecture bodies; no xparse/expl3 in content files.
- Overlay specs are optional slide polish; the web target flattens them.
- Sized delimiters split across alignment rows: use balanced-per-row
  `\left…\right.` / `\left.…\right]` fences — never split a `\Big`-family
  pair across rows (this corrupted MathML in the donor project).
- Circled labels: use the kit's `\case{N}` (renders ① in slides, "(N)" on the
  web) — never raw `\textcircled` in content.
- Display equations: break long equations at the source (chain-split at `=`,
  `\qquad` pairs → `gathered`, product continuations with `\times`/`\cdot`);
  browser font metrics differ, so leave generous width margin.

## Figures & alt text
- Every figure authored via `\fig{path}{alt-key}`; description written into
  the `alt/` sidecar in the same session the figure is made.
- A figure shared across lectures is owned by the lecture that introduced it;
  its alt text lives with the owner.

## Announcements
- Never in lecture bodies — per-lecture sidecars in `announcements/`, absent
  file means no announcements frame.
