# Troubleshooting — when a gate fires

`course.py` runs these checks on every build. Each row: what the symptom
means and the first move. Most of these encode failures that have actually
happened; the fix patterns are proven.

| Symptom | Meaning | Fix |
|---|---|---|
| `make: no .tex files with \documentclass` / nothing builds | the root `lectureNN.tex` wrappers are missing (BookML's scan needs them; they're generated, not committed) | build through `./course.py build NN` — it (re)generates wrappers |
| latexml log: `undefined ... \something` | the content uses a construct outside the kit subset | check `docs/authoring.md`'s palette + banned list; add the macro to `shared/macros.tex` (or a shim to `shared/preamble-web.tex` if it's a rendering construct) |
| image-depth errors (`could not find depth for BookML image ...`) | dvisvgm has no Ghostscript **library** (libgs), so figure baselines can't be read | `brew install ghostscript` (or distro equivalent); harmless meanwhile — baseline alignment only, and `check` says so rather than failing |
| `[ALT MISSING: key]` in a page / check failure | a figure's description isn't in the owner's sidecar | add `\setfigalt{lectureNN/name}{...}` to `alt/lectureNN.tex`; if the figure is borrowed, the borrowing lecture needs `\usealtfrom{lectureMM}` |
| figure `<img>` with EMPTY `alt` | the alt bridge didn't run — `\fig` bypassed, or `\kitfigdesc` no longer follows the figure input | use `\fig` (never bare `tikzpicture` for content figures); check `shared/preamble-web.tex`'s `\fig` is intact |
| `bare-math-text > 0` | character data directly inside a non-token MathML element — the malformed-MathML signature | isolate the formula; known causes: sized fences split across alignment rows, exotic color specs in math. Fix the construct; if the formula is genuinely clean, it's an engine bug — record and report upstream |
| pa11y: color-contrast on text inside a figure | TikZ text leaked into the DOM — the figure was NOT imaged (BookML's `bmlimages` inactive) | `./course.py doctor`: is `bookml/` present? is `\bmlImageEnvironment{tikzpicture}` still in `shared/preamble-web.tex`? rebuild |
| pa11y: scrollable-region / equation overflows | a display equation is wider than the column | **break the equation in the content** (patterns in `docs/authoring.md`); never suppress the audit rule — it is the too-long-equation tripwire |
| high `unparsed` count in checks | formulas missing LaTeXML's math grammar, rendered as flat-but-valid token runs | cosmetic: alttext and rendering are intact. Rewrite a formula only if it *looks* wrong. Typical rate: ~0.5–6% per lecture |
| `unparsed` climbs by exactly the number of `±`-branch or stacked-case labels you just added | two related MathML-grammar traps: `\genfrac{}{}{0pt}{}{...}{...}` used to *stack* case labels is unparseable, and a fragment like `$+ \to \Gamma_1$` is a unary `+` with no operand | don't stack with `\genfrac` — put the branch assignment in a following sentence; and give each fragment a real operand, e.g. "the eigenvalue $+1$ labels $\Gamma_1$". Both fixes read better aloud too |
| `slides NN` fails with `overfull > 2pt`, or reports `boxes: N overfull` | a frame's content exceeds the slide — beamer clipped (or will clip) it. `slides` parses the build log **before** cleanup and fails on any box beyond sub-line tolerance; residuals ≤2pt are reported but benign. (Historical note: before this check, `latexmk -c` deleted the log first, an empty grep read as "clean", and an 18.6pt clipped frame hid behind four green builds — a check whose pass is an empty grep must be shown to fail when it should) | the offending `Overfull` lines are printed and the full log is retained at `build/slides/lectureNN-slides.log`; render the frame, then re-lay — split it, use `columns`, or cut a whole rendered line (next row). Never shrink type first. If it prints `boxes: NOT CHECKED`, latexmk skipped the build: `./course.py clean`, rebuild |
| a frame is a few pt overfull and trimming words does nothing | line count, not word count, sets the height — cuts that re-wrap to the same number of rendered lines change nothing | render the frame, count the rendered lines, and cut enough to remove a whole one (target the item with a short orphan tail). Or re-lay with `columns`; shrinking type is the last resort |
| `Command \foo already defined` in a lecture you did not touch, right after promoting a macro to `shared/macros.tex` | promotion is **two** edits and only one was made: `shared/macros.tex` loads before every lecture body, so `\providecommand` there wins and the donor lecture's surviving local `\newcommand` then collides | delete the local definition from the lecture that had it, then re-run **that** lecture's `build` *and* `slides` — promoting a macro is a cross-lecture change, so the donor lecture is part of the blast radius |
| `Missing $ inserted` on a line whose only oddity is `\alert{...}` | `\alert` takes **text**-mode content; math inside it needs its own `$…$` | `\alert{$x \in [-\frac12,\frac12)$}`, or lift the emphasised formula out of the surrounding display |
| announcements don't appear on the web | by design — announcements are slides-only ephemera | `./course.py build NN --keep-announcements` for a one-off web copy |
| content missing from the web page that shows on slides | `\only<closed-range>` — closed ranges mean "not in the final state" and are dropped | if the content should persist, use `\onslide<n->` or an open range |
| figures stale after editing TikZ | `bmlimages/` is a render cache keyed to the DVI | `./course.py clean --deep` (drops the cache), then rebuild |
| white-backed figure labels render as solid coloured boxes | a bare colour name in a node's option list (`\node[lbl, physgreen]`) sets `color=`, which also sets the **fill** — silently overriding the `fill=white` that came from the node style | colour the text explicitly: `\node[lbl, text=physgreen]`. Same trap for any style that sets `fill` and is then combined with a bare colour name |
| a figure shrunk to fit a frame has labels that look too large | TikZ `scale=` scales coordinates but **not** text nodes, so labels keep their absolute size as the drawing shrinks | shrinking is not a density fix — re-lay the frame instead (e.g. put two equation blocks in `columns`) and keep the figure legible |
| slides green, web broken (or vice versa) | something target-specific crept into the single source | this is exactly what the dual-target regression gate catches; diff your constructs against `content/lecture00.tex` and the palette table |
| hacking preambles: a `\titlepage`-style override silently ignored on the web | LaTeXML re-establishes some class commands after the preamble | override inside `\AtBeginDocument{...}` (see `shared/preamble-web.tex` for the worked instance) |

## Reading the logs

- Web build: `build/logs/lectureNN.make.log` (the make run) and
  `build/web/latexmlaux/lectureNN.latexml.log` (the conversion — grep
  `^Error` / `^Warning`).
- Slides: latexmk output is in `build/slides/`.
- `./course.py check NN` re-runs every gate on an existing build without
  rebuilding.
