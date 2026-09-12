# phys-course-kit

A template repository for publishing a physics lecture course as an
**accessible website** — HTML5 with native MathML (math a screen reader
reads out directly, rather than images of equations or JavaScript that
draws them), figures as SVG images with author-written alt text, and a set
of checks every build has to pass — with an optional, matching **beamer
slide deck** per lecture from the same source.

**Who this is for:** a LaTeX-competent physicist. No prior experience with
this kit — or with directing AI — is assumed.

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

Each lecture is **one authored file** — `content/lectureNN.tex`, built out
of frames and limited to the LaTeX that both the web build and the slide
build understand (the worked example is
[`content/lecture00.tex`](content/lecture00.tex)) — by the assistant during
transcription, or by you directly. Two short build files render it:

```
content/lectureNN.tex ──┬─▶ drivers/web.tex    → LaTeXML + BookML → accessible HTML
                        └─▶ drivers/slides.tex → beamer           → PDF deck (optional)
```

Everything hand-written beyond the lecture itself lives in small companion
files, which the kit calls sidecars: figure descriptions in `alt/` (a
missing description is a build **error**, not a rendering quirk), and
day-of-lecture announcements in `announcements/` (they appear on the
slides, never in the published archive). Even if you never lecture from
slides, the slide version is built as a check — it proves each lecture
still works both ways, so nothing web-only or slides-only can creep into
your source. If you do lecture from slides, say so once in
`shared/course.tex`, and the slide build then also checks that every frame
fits on its slide.

The published site uses a single light colour scheme over BookML's plain
theme; a dark theme waits on a plan for the colours inside the SVG figures.

## Quick start

Three things the steps below assume: a GitHub account; a copy of the
repository on your computer (after step 1, GitHub's green **Code** button
offers "Open with GitHub Desktop" or "Download ZIP" if you have never used
`git`); and a terminal — on macOS, the Terminal app — opened in the
repository's folder, which is where every command below is typed.

1. Press **Use this template** on GitHub and clone your new repository.
2. Edit [`shared/course.tex`](shared/course.tex) — course code, title, term,
   URL, and whether you lecture from slides. That is the only renaming
   there is.
3. `./setup.sh` — checks that the software the kit needs is installed (TeX
   Live, LaTeXML, Ghostscript, pa11y), asks before installing anything, and
   fetches BookML at one fixed, checksum-verified release.
4. `./course.py build 00` — the sample lecture should print `PASS`, with
   every check passing. `./course.py doctor` explains anything that doesn't.
5. Put your lecture source material — scanned notes, PDFs — in `source/`,
   one file per lecture named `lectureNN.pdf` (`lecture01.pdf`, …); it
   stays out of git.
6. Open the repository in your agentic AI tool (the kind described under
   "How the work gets done" above) and tell it:
   *"Read AGENTS.md, then begin lecture 1 from source/lecture01.pdf."*
   The assistant runs the transcription stages and interviews you along the
   way; [`WORKFLOW.md`](WORKFLOW.md) describes your side of that
   loop. Working without an assistant instead? Copy the shape of
   [`content/lecture00.tex`](content/lecture00.tex) under the rules in
   [`docs/authoring.md`](docs/authoring.md). (Either way: delete the
   `lecture00` sample files before your first real publish.)

A standard TeX Live plus LaTeXML, installed so that both run in your
terminal, is all that's expected — no particular TeX version to chase, no
version juggling.

## Layout

| Path | What it holds |
|---|---|
| `source/` | Your raw lecture material (scans, notes PDFs) — untracked by git |
| `content/` | Canonical lecture files — the only authored LaTeX (assistant- or hand-written) |
| `figures/` | TikZ figure sources, one directory per owning lecture |
| `alt/` | Figure alt-text sidecars, written when the figure is made |
| `announcements/` | Per-lecture, day-of-editable, slides-only |
| `drivers/` | The two short build files (web primary, slides optional) |
| `shared/` | Course identity, macros, the two preambles, the palette |
| `notes/` | Per-lecture transcription work records (make batches resumable) |
| `WORKFLOW.md` | **Your manual**: the loops you're part of — reviews, day-of-lecture, publishing |
| `AGENTS.md` | The AI assistant's operating manual (`CLAUDE.md` is a pointer stub for Claude-family tools) |
| `docs/` | Reference shelf — setup details, authoring rules, what each failed check means; the assistant works from these, you dip in as needed |
| `CHANGELOG.md` | The kit's release notes — and, in your course, the append-only course ledger (rules inside) |
| `conventions.md` | Your course's durable decisions, as they get made |
| `course.py` | The one command that builds, checks, and reports on everything |
| `setup.sh` | Day-0 check of the software the kit needs, and the BookML fetch — asks before installing anything |
| `GNUmakefile` | Configuration for BookML (a make-based tool that `course.py` runs for you) — you never run `make` yourself |
| `LICENSE` | MIT — use, copy, and adapt freely |

## What gets checked

Every `./course.py build NN` runs the full set of checks on the result: the
conversion log is scanned for errors, every figure must carry its alt text,
the MathML is checked for a known way it can come out malformed, no slide
overlay mark may have leaked onto the page as text, and each
page gets an automated accessibility audit (axe, via pa11y — `setup.sh`
offers to install it; without it the build still produces the page and
prints a warning with install instructions, and that page has not been
audited). A lecture that passes is publishable; `./course.py build --all` produces the whole site
plus its index under `build/web/html/`, ready for any web host that serves
plain files.

## Provenance

The kit is the distilled workflow of a real 26-lecture graduate course
(PHYS 567, *Geometry and Topology in Modern Electronic Structure Theory*),
which went from handwritten notes to validated accessible HTML. Before
and after each release, fresh AI assistants have re-authored lectures of
that course from the handwritten pages using only this repository, and
their results have matched the validated versions; what those runs
taught is folded into the manual, the conventions, and the checks.
Release notes: `CHANGELOG.md`; the full development record is in this
repository's git history.
