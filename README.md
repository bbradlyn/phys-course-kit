# phys-course-kit

A template repository for turning handwritten physics lecture notes into an
**accessible HTML course site** (HTML5 + native MathML + SVG figures with
authored alt text), with an optional beamer slide deck per lecture — designed
so that a new course can start producing validated, accessible pages from
lecture 1, without re-learning anything the hard way.

**Who this is for:** a LaTeX-competent physicist working with a capable AI
assistant (Claude Opus-class or better). Neither of you needs prior experience
with this pipeline — the experience is written down here. The human guide lives
in [`docs/`](docs/); the AI assistant's operating manual is
[`CLAUDE.md`](CLAUDE.md), which any capable agent should read before touching
course content.

## Architecture: one source, two drivers, no transform

```
content/lectureNN.tex        ← the ONLY authored lecture file (engine-neutral:
      │                        frames, blocks, \fig{path}{alt-key}, course macros)
      ├── drivers/web.tex    → LaTeXML + BookML → accessible HTML  (PRIMARY)
      └── drivers/slides.tex → beamer → PDF deck                   (OPTIONAL)
```

There is **no transform step**: both targets `\input` the same content file
through thin driver wrappers. The slides target is built headlessly as a
regression gate even if you never lecture from slides — it proves the content
stays inside the dual-compatible subset. Ephemeral material (announcements,
dates) lives in per-lecture sidecars under [`announcements/`](announcements/),
never in lecture bodies. Every figure is born with alt text in
[`alt/`](alt/) sidecars — a missing description is a build error, not a
rendering quirk.

## Layout

| Path | What it holds |
|---|---|
| `content/` | Canonical lecture sources — the only files you author |
| `figures/` | TikZ figure sources, shared namespace from the start |
| `alt/` | Figure alt-text sidecars, written at transcription time |
| `announcements/` | Per-lecture day-of-editable sidecars (slides-only) |
| `drivers/` | The two thin build wrappers (web primary, slides optional) |
| `shared/` | Course macros, the two preambles, site CSS |
| `docs/` | The human guide: setup, authoring, workflow, troubleshooting |
| `CLAUDE.md` | The AI assistant's operating manual |
| `CHANGELOG.md` | Append-only project ledger (rules inside — keep the discipline) |
| `conventions.md` | Durable conventions distilled as the course proceeds |

## Status

**Under construction (started 2026-08-02).** This kit is being extracted from
PHYS 567 "Geometry and Topology in Modern Electronic Structure Theory"
(26 lectures, fully validated accessible-HTML archive) and from its
LaTeXML/BookML engine pilot. The acceptance test for the kit is a complete
worked example: PHYS 567's lecture 25 re-authored in kit format, building both
targets clean through the full validation gate suite and matching its
known-good reference output. Design record: the donor repo's
`streamlining.md` §8–§9.

Not yet present (arriving with extraction): `course.py` (the one-command
driver), the preambles and macro layer, the setup script, the guide chapters'
full content, and the worked example itself.
