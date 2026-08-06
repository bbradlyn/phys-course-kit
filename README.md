# phys-course-kit

A template repository for publishing a physics lecture course as an
**accessible website** — HTML5 with native MathML (no JavaScript renderers),
figures as SVG images with author-written alt text, and a validation suite
that gates every build — with an optional, matching **beamer slide deck** per
lecture from the same source.

**Who this is for:** a LaTeX-competent physicist. No prior experience with
this pipeline — or with directing AI — is assumed.

**How the work gets done:** the transcription workflow is designed around an
*agentic* AI tool — one that works inside a repository: reading files,
running commands, editing sources (Claude Code, Codex CLI, Cursor, and
similar; any capable one, not one vendor's). You open this repository in
such a tool; the assistant reads [`AGENTS.md`](AGENTS.md) — its operating
manual — and does the production work in stages, stopping at fixed points to
ask you questions and show you drafts. Your side of that loop — the answers,
reviews, and sign-offs — is described in [`WORKFLOW.md`](WORKFLOW.md).
(A `CLAUDE.md` stub points Claude-family tools at the same manual. And no
assistant is required: everything can be hand-authored —
[`content/lecture00.tex`](content/lecture00.tex) is the format,
[`docs/authoring.md`](docs/authoring.md) the rules, and `course.py` builds
and checks your work the same way.)

## How it works

Each lecture is **one authored file** — `content/lectureNN.tex`, written in
a frame-structured, engine-neutral LaTeX subset (the worked example is
[`content/lecture00.tex`](content/lecture00.tex)) — by the assistant during
transcription, or by you directly. Two thin wrappers render it:

```
content/lectureNN.tex ──┬─▶ drivers/web.tex    → LaTeXML + BookML → accessible HTML
                        └─▶ drivers/slides.tex → beamer           → PDF deck (optional)
```

Everything hand-written beyond the lecture itself lives in sidecar files:
figure descriptions in `alt/` (a missing description is a build **error**,
not a rendering quirk), and day-of-lecture announcements in
`announcements/` (they appear on the slides, never in the published
archive). Even if you never lecture from decks, the slide build runs as a
check — it proves each lecture still renders on both targets, so nothing
web-only or slides-only can creep into your source.

## Quick start

1. Press **Use this template** on GitHub and clone your new repository.
2. Edit [`shared/course.tex`](shared/course.tex) — course code, title, term,
   URL. That is the only renaming there is.
3. `./setup.sh` — checks the toolchain (TeX Live, LaTeXML, Ghostscript,
   pa11y), asks before installing anything, and fetches BookML at a pinned,
   checksum-verified release.
4. `./course.py build 00` — the sample lecture should PASS with every gate
   green. `./course.py doctor` explains anything that doesn't.
5. Put your lecture source material — scanned notes, PDFs — in `source/`
   (it stays out of git).
6. Open the repository in your agentic AI tool and tell it:
   *"Read AGENTS.md, then begin lecture 1 from source/lecture01.pdf."*
   The assistant runs the transcription stages and interviews you along the
   way; [`WORKFLOW.md`](WORKFLOW.md) describes your side of that
   loop. Working without an assistant instead? Copy the shape of
   [`content/lecture00.tex`](content/lecture00.tex) under the rules in
   [`docs/authoring.md`](docs/authoring.md). (Either way: delete the
   `lecture00` sample files before your first real publish.)

A standard TeX Live plus LaTeXML on PATH is all that's expected — no pinned
TeX installs, no version juggling.

## Layout

| Path | What it holds |
|---|---|
| `source/` | Your raw lecture material (scans, notes PDFs) — untracked by git |
| `content/` | Canonical lecture files — the only authored LaTeX (assistant- or hand-written) |
| `figures/` | TikZ figure sources, one directory per owning lecture |
| `alt/` | Figure alt-text sidecars, written when the figure is made |
| `announcements/` | Per-lecture, day-of-editable, slides-only |
| `drivers/` | The two build wrappers (web primary, slides optional) |
| `shared/` | Course identity, macros, the two preambles, the palette |
| `notes/` | Per-lecture transcription work records (make batches resumable) |
| `WORKFLOW.md` | **Your manual**: the loops you're part of — reviews, day-of-lecture, publishing |
| `AGENTS.md` | The AI assistant's operating manual (`CLAUDE.md` is a pointer stub for Claude-family tools) |
| `docs/` | Reference shelf — setup details, authoring rules, the gate table; the assistant works from these, you dip in as needed |
| `CHANGELOG.md` | Append-only course ledger (rules inside — keep the discipline) |
| `conventions.md` | Your course's durable decisions, as they get made |
| `course.py` | The one-command driver: every build, check, and report |
| `GNUmakefile` | Configuration for BookML (a make-based tool `course.py` drives) — you never run `make` yourself |

## What the gates check

Every `./course.py build NN` runs the full suite on the result: the
conversion log is scanned for errors, every figure must carry its alt text,
the MathML is checked for a known malformation signature, and each page gets
an automated accessibility audit (axe, via pa11y). A lecture that passes is
publishable; `./course.py build --all` produces the whole site plus its
index under `build/web/html/`, ready for any static host.

## Provenance

The kit is the distilled pipeline of a real 26-lecture graduate course
(PHYS 567, *Geometry and Topology in Modern Electronic Structure Theory* —
handwritten notes to validated accessible HTML), rebuilt in the simplified
form that experience suggested. It was acceptance-tested end to end: a
fresh AI agent, given only this repository's manual and thirteen pages of
handwritten notes, re-authored one of that course's lectures through the
full workflow — interviews, figures, alt text, gates — and the result
matched the course's validated version on every content check. (One
difference favored the kit: its computed band-structure figure exposed a
drawing error in the original.) The web output layers a light
course-palette style over BookML's plain theme — frame cards, palette
headings, sticky page navigation — in a single forced-light scheme (a real
dark theme awaits an SVG figure-palette strategy). Development history:
`CHANGELOG.md`.
