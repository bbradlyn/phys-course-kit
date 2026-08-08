# Conventions

Durable rules distilled from the changelog — forward-propagating: once a
convention lands here, all future lectures follow it (earlier ones are
retrofitted only by explicit decision). Seeded with proven rules; grows as the course proceeds.

Record **terminology and presentation preferences here too, not just
notation** — established house names for recurring objects, house table
styles for systematic data. The reason: a faithful
transcription agent reproduces the *source* wherever the house style isn't
written down — fidelity forbids it from inventing style.

## Authoring (engine-neutral content subset)
- Frames, blocks, columns, overlay specs, and course macros only — no
  target-specific code in lecture bodies; no xparse/expl3 in content files.
- Overlay specs are optional slide polish; the web target flattens them.
- Sized delimiters split across alignment rows: use balanced-per-row
  `\left…\right.` / `\left.…\right]` fences — never split a `\Big`-family
  pair across rows (this corrupts the generated MathML).
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
- **Never stack case labels with `\genfrac`** (a zero-thickness fraction used to
  put `+ \to \Gamma_1` over `- \to \Gamma_2`). LaTeXML cannot parse it and the
  formula drops out of parsed MathML — same failure family as the labelled-matrix
  rule above. Put the branch assignment in a following sentence instead.
- **A math fragment must be a complete expression.** `$+ \to \Gamma_1$` is a
  unary `+` with no operand and goes unparsed; name the eigenvalue instead —
  "the eigenvalue $+1$ labels $\Gamma_1$". This bites whenever a board `±`
  branch is split into its two cases.
- **Character tables are real tables**, never matrices or aligned math: a
  `tabular` with `\toprule`/`\midrule`/`\bottomrule` (booktabs is loaded on both
  targets), irrep label in the first column, one column per class, wrapped in
  `center`. Same reasoning as the labelled-matrix rule — a screen reader gets
  proper row and column structure.

## Example entries: notation (replace with your course's own decisions)

Worked examples of the right granularity for this file — delete them as
your course makes its own calls. (A course that adopts an example makes it
**binding** by rewriting this section in its own first batch — until then, an
assistant reads these as template filler, not house style.)

- *Example:* Pauli matrices carry **superscript** indices: `\sigma^0`
  (identity), `\sigma^x,\sigma^y,\sigma^z`; `\tau^a` for a second two-level
  (sublattice) space; `\vec\sigma` for the Pauli vector. Sources written with
  subscripts are converted silently.
- *Example:* Time reversal is $\mathcal{T}$ (macro `\TRS`); complex
  conjugation is $\mathcal{K}$ (macro `\conj`).
- *Example:* Upright space-group symbols via an `\sg{...}` macro —
  lecture-local at first, promoted to `shared/macros.tex` as
  `\providecommand` the first time a second lecture wants it (the standard
  promotion path for any macro).
- *Example:* A mirror's subscript names its plane **normal**; keep
  Hermann–Mauguin-style indices so students can find the group on the Bilbao
  server.
- *Example:* `\vec e_1,\vec e_2` for primitive vectors, `\vec R` for Bravais
  translations; Dirac notation only via `\ket`/`\bra`/`\braket`; say
  "irreps", never "irreducibles".
- *Example:* The **reciprocal-lattice** translation group is $\check T$
  (`\check T`), distinguished by the check accent from the direct-lattice
  translation group $T$. Gloss it in words the first time a lecture uses it.
- *Example:* Seitz symbols are written `\{g|\vec d\}`; barred symbols ($\bar g$, $\bar G_k$)
  are the cogroup elements, i.e. the point-group parts modulo translations.

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
- **Never encode meaning by colour alone.** Pair colour with position, shape,
  a label, or line style — the figure must read identically to colour-blind
  students and in a grayscale printout.
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
- **Multi-state figures (a figure revealed in stages) are two files with a pinned,
  identical bounding box.** Put `\useasboundingbox (x1,y1) rectangle (x2,y2);` with
  the *same* rectangle at the top of every state, or the picture rescales and jumps
  between overlays. Everything structural — axes, all ticks, and any annotation the
  argument leans on — goes in *every* state as an always-on layer, so only the
  content under discussion changes. Select them with
  `\only<1>{\fig{...-half}{...}}` and `\only<2->{\fig{...}{...}}`: the closed range
  is dropped by the web target (correct — a partial state is a teaching view), and
  the **open** range is what makes the real figure survive flattening. Give the
  partial state its own alt entry anyway.
- `columns` reserves **no trailing vertical space** — body text placed after
  `\end{columns}` collides with the tallest column. Follow it with `\medskip`.
- When two figures show the same path or region, they must label it
  identically. Symmetry-equivalent representatives are a free choice, which is
  precisely why the choice has to agree across figures: a student who sees
  different labels will hunt for a difference that is not there.

## Announcements
- Never in lecture bodies — per-lecture sidecars in `announcements/`, absent
  file means no announcements frame.
