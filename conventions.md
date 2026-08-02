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
- **Labelled matrices: never border a matrix with floating row/column labels**
  (`\bordermatrix`, or a hand-built array of label cells). Those labels are
  visual-spatial information that reads badly or not at all for a screen-reader
  user, and they drop the formula out of parsed MathML. Use a plain
  `pmatrix`/`smallmatrix` and name the basis in the introducing sentence —
  "in the sublattice basis $(A,B)$, …" — which serves every reader identically.
- Boxed callouts on the source board are *emphasis*, not titled results:
  render them with `\alert{...}`. Reserve `block`/`alertblock` for material the
  source actually gave a title; inventing a title to justify a block would
  breach prose fidelity.
- Write tensor products explicitly (`\otimes`) even where the source juxtaposes
  the factors, so the product can never be misread as a matrix product.

## Notation (physics)
- Pauli matrices carry **superscript** indices: `\sigma^0` (identity),
  `\sigma^x,\sigma^y,\sigma^z`; `\tau^a` for the sublattice two-level space;
  `\vec\sigma` for the Pauli vector. Sources written with subscripts are
  converted silently.
- Time reversal is $\mathcal{T}$ (macro `\TRS`); complex conjugation is
  $\mathcal{K}$ (macro `\conj`).
- Upright space-group and little-group symbols via `\sg{...}` (= `\mathrm`).
  Lecture-local in `lecture25`; promote to `shared/macros.tex` as
  `\providecommand` the first time a second lecture wants it.
- A mirror's subscript names its plane **normal** — $M_{1\bar1}$ is the plane
  with normal $\vec e_1-\vec e_2$. Keep the Hermann–Mauguin-style index: it is
  what students use to find the group on the Bilbao server.
- `\vec e_1,\vec e_2` for primitive vectors, `\vec R` for Bravais translations;
  Dirac notation only via `\ket`/`\bra`/`\braket`. Say "irreps", not
  "irreducible representations".

## Frame structure
- `\announcementsframe` goes directly after the title frame.
- Every lecture ends with a **static** Takeaways frame (no reveals).

## Figures & alt text
- Every figure authored via `\fig{path}{alt-key}`; description written into
  the `alt/` sidecar in the same session the figure is made.
- A figure shared across lectures is owned by the lecture that introduced it;
  its alt text lives with the owner.
- **Alt text is richly descriptive: it carries what the figure *argues*, not
  just what it depicts.** If the picture makes an argument (an even-vs-odd
  crossing count, a cancellation, a limit), the description states it — a
  reader who cannot see the panel must be able to reach the same conclusion.
- Reproduce what a source drawing *says*, not every pen stroke. Board marks
  that record the lecturer's thinking (traversal arrows, lassos, underlines)
  are omitted unless they carry content.
- **Colour a TikZ node's text with `text=<colour>`, never a bare colour name.**
  A bare colour in a node's option list sets `color=`, which also sets the
  fill and silently overrides a `fill=white` coming from the node style;
  white-backed labels then render as solid coloured boxes.
- Labels that must stay legible over a busy drawing (a lattice net, a shaded
  region) get a white-filled node:
  `lbl/.style={fill=white, inner sep=1pt, font=\small}`.
- TikZ `scale=` does **not** scale text nodes, so shrinking a figure to fit a
  frame makes its labels relatively *larger*. Shrinking is not a free density
  fix — re-lay the frame instead (e.g. `columns`).
- When two figures show the same path or region, they must label it
  identically. Symmetry-equivalent representatives are a free choice, which is
  precisely why the choice has to agree across figures: a student who sees
  different labels will hunt for a difference that is not there.

## Announcements
- Never in lecture bodies — per-lecture sidecars in `announcements/`, absent
  file means no announcements frame.
