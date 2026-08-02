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
