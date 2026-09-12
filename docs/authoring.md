# Authoring guide — what goes in a lecture file, and why

Reference for whoever writes lecture content — normally the AI assistant
during transcription, and you whenever you author or edit by hand. "You"
below means the author of the moment; the rules bind both of you equally.

Each lecture is exactly one file: `content/lectureNN.tex`, written in the
LaTeX that both the web build and the slide build understand.
`content/lecture00.tex` is the living reference — copy its shape. Rules
below carry their reasons.

## Anatomy of a lecture file

```latex
\kitlecturetitle{Topic Title}          % first line: title metadata
% \usealtfrom{lectureMM}               % only if reusing another lecture's figures

\begin{frame}                          % title frame
  \titlepage
\end{frame}

\announcementsframe                    % renders on slides only; sidecar-driven

\section{First Part}                   % h2 / part divider

\begin{frame}{A Frame Title}           % h3 / a slide (a <section> on the web)
  ...
\end{frame}
...
\section{Takeaways}
\begin{frame}{Takeaways} ... \end{frame}
```

## What you can use in a lecture file

| Construct | Slides render | Web renders |
|---|---|---|
| `\section{...}` | section marker | numbered `h2`, part divider |
| `\begin{frame}{Title}` | a slide | `h3` + its own `<section>` |
| `block` / `alertblock` / `exampleblock` | styled box | bold-title paragraph (semantic containers planned) |
| `columns` / `column` | side-by-side | stacked top-to-bottom, reading order |
| `itemize` / `enumerate` / `description` | native (overlay specs honored) | native (specs stripped) |
| `\item<2->`, `\onslide<2->{...}`, `\uncover`, `\visible`, `\pause` | progressive reveal | final state |
| `\only<spec>{...}` | shown only on those overlays | **kept iff the range is open** (`<2->`); closed ranges (`<1>`, `<1-2>`) are staging and are dropped |
| `\alt<spec>{on}{off}` | *on* text during `spec`, *off* text otherwise | the *on* text, always |
| `\alert{...}` | orange emphasis (text; an inline formula inside needs its own `$…$`) | bold + orange |
| `\boxed{...}` (inside math) | framed formula | framed formula (a MathML box) |
| `\case{N}` | circled glyph ① | `(N)` |
| `\fig{path}{alt-key}` | centered figure | dvisvgm SVG `<img>` with the sidecar text as `alt` |
| `\figw{width}{path}{alt-key}` | `\fig` capped to `width` (scales text too, unlike TikZ `scale=`) | same as `\fig` (images flow at page width) |
| `\announcementsframe` / `\announcementsblock` | sidecar content | nothing (by construction) |

Overlays are **optional slide polish** — write them if you lecture from the
deck; the web build always flattens to the final state. Careful with `\only`:
its closed-range semantics are the one overlay construct that *removes*
content from the web (that is its meaning — content the final state doesn't
show). If in doubt, use `\onslide`.

## Math

- Display math: `\[...\]`, `equation`, `align*`, `gathered`, `aligned` — all
  fine. Inline `$...$`.
- **Break long display equations at the source.** Patterns that work: split
  chains at `=` (`aligned`/`align*`), turn `A \qquad B` two-clause displays
  into `gathered`, continue products with a leading `\times`/`\cdot` on the
  next row. Browser math fonts differ by ~5%, so leave real width margin —
  if an accessibility audit ever flags a scrollable equation, the fix is
  breaking that equation, not suppressing the audit.
- **Sized delimiters must balance within each alignment row.** Splitting a
  `\Bigl[ ... \Bigr]` pair across rows corrupts the generated MathML (the
  classic trap). Use `\left[...\right.` on the
  first row and `\left....\right]` on the continuation.
- A small share of formulas (typically ~0.5–6% per lecture) miss LaTeXML's
  math grammar and render as flat-but-valid token MathML. Cosmetic; rewrite
  only if the rendering actually looks wrong.

## Figures and alt text

- Every figure: `\fig{figures/lectureNN/name}{lectureNN/name}` — path and alt
  key. TikZ source in `figures/lectureNN/`, description in
  `alt/lectureNN.tex` (`\setfigalt{lectureNN/name}{...}`), **written in the
  same session the figure is made**. `[ALT MISSING]` is a build failure.
- A figure is *owned* by the lecture that introduced it. Reusing it later:
  keep the original path and key, and declare `\usealtfrom{lectureMM}` at the
  top of the borrowing lecture — one description per figure, maintained once.
- Write alt text as a description of what the figure shows and means, not a
  terse caption ("A square lattice of sites with the two primitive vectors
  drawn from one site", not "The lattice"). The reader who can't see the
  figure gets *only* this.
- Figure text is rendered inside the image (glyphs, not live page text), so
  use the kit palette freely; the alt text carries the meaning.

## Banned in content files (each bans a real failure)

| Never | Because |
|---|---|
| xparse (`\NewDocumentCommand`) or expl3 in content or local macros | the web engine cannot parse them; the kit preambles are classic TeX by construction |
| raw `\textcircled{...}` | the web engine mangles decorated arguments; use `\case{N}` |
| version-specific branches (`\ifdefined\HCode`-style hacks) | one source feeding both outputs is the whole design; if a construct only works in one of them, raise it as a conventions question |
| announcements/dates in lecture bodies | they belong in `announcements/lectureNN.tex`; the archive stays timeless |
| splitting `\Big`-family fences across rows | the MathML corruption above |

## Course macros

Math macros live in `shared/macros.tex` (only macros that mean the same
thing in both outputs). A macro used by a single lecture may start as a
`\newcommand` at the top of that content file. Promote it to
`shared/macros.tex` the first time a second lecture wants it — and
promotion is **two edits**: add it there as `\providecommand`, *and* delete
the local definition from the lecture that had it. The shared file loads
before every lecture body, so a surviving local `\newcommand` collides
(`Command \foo already defined` — the troubleshooting table has the row);
`\providecommand` in the shared file does not protect it. Re-run that
lecture's `build` and `slides` afterwards, and record the promotion in
`CHANGELOG.md`. Notation decisions that bind later lectures go in
`conventions.md` when they're made.
