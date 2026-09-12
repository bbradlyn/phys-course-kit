# Changelog

This file has two jobs.

**In this template repository** it is the kit's release notes: features and
fixes, newest first, below the rule.

**In a course built from the template** it becomes the course's ledger.
Start your own table here, above the rule; the kit's release notes below it
can stay for reference or go whenever you are ready — deleting them is your
call, not the assistant's:

```markdown
| Date | Decision / Update |
| --- | --- |
```

Ledger rules — they are what make the workflow auditable: **append-only**
(add new rows; never edit or reorder past ones); every session that changes
course content or process appends a row (`AGENTS.md`, contract #6); a batch
without its ledger row is not done. Durable conventions distilled from the
log live in `conventions.md`.

---

## 2026-09-12 — Slides become opt-in; documentation pass before going public

### Changed

- **S4 is checks and sign-off; S5 is the slides stage, and only for courses
  that lecture from slides.** Progressive reveals, splitting frames to fit a
  slide, and the author polish round now live together in one stage that a
  web-only course never enters — such a course may be transcribing
  narrative notes purely for an accessible web version, and it no longer
  has to fit anything onto a slide. Overlays were already documented as
  optional slide polish that the web flattens; the workflow still authored
  them in the required path, a leftover from the deck-first course the kit
  was distilled from. A signed-off S4 batch is the finished lecture, and S4
  keeps every web check, the automated accessibility audit included.
- **`\coursedecks` in `shared/course.tex`** says whether the course lectures
  from slides (`no` unless you say otherwise). `./course.py slides NN`
  always builds the slide version — it is the check that one source still
  works both ways — and always prints the overfull-frame report; it fails
  on an overfull frame only when `\coursedecks` is `yes`. `doctor` reports
  the setting.
- The human-facing documents (`README.md`, `WORKFLOW.md`, `docs/setup.md`)
  are written for a LaTeX-competent physicist with no programming or AI
  experience required: build-engineering vocabulary ("gate", "regression",
  "CI", "toolchain") replaced with plain words, and the reference shelf
  (`docs/`) lightened the same way. `AGENTS.md` opens with a note for an
  assistant working on the kit itself rather than on a course, carrying
  the two standing rules: the template is self-contained, and the human
  documents stay in plain words.

### Fixed

- The README's provenance section no longer narrates the development
  history (page counts, individual bugs, kickoff phrases); the release
  notes and git history carry that.
- The changelog header no longer tells a course to delete the kit's
  release notes as its first step: the ledger starts above them, and the
  deletion is the owner's, whenever they are ready.
- **`\item<n->` leaked its overlay spec onto the web page as text**
  (`¡2-¿`) in every list — the kit's own sample lecture included — because
  LaTeXML rebinds `\item` when a list begins, past the kit's wrapper. A
  LaTeXML binding (`shared/kitoverlay.sty.ltxml`) now strips the spec where
  the rebinding happens, and a new check
  (`overlay-leak`) fails any build that prints an overlay spec; it was shown
  to fail on the old output before the fix. Found by an assistant reading
  its own page in a trial run.
- Boxed equations keep their box. The conventions seed told the assistant
  to render every board box as `\alert` emphasis, which dropped the box
  from boxed equations; it now distinguishes a boxed equation
  (`\boxed{...}`, which renders on both targets) from boxed prose
  (`\alert`). Found when the author read a trial run's first page.
- A missing pa11y no longer passes silently. `build` and `check` printed
  `pa11y: clean` when pa11y was not installed and the audit had not run at
  all; they now print a warning with install instructions, still produce
  and check the page, and say on the `PASS` line that the audit was
  skipped (`--strict` still makes it a failure, for automated runs). The
  audit needs Node.js, which not every machine — or assistant — can
  install, so the page is never held hostage to it.
- `docs/authoring.md` still carried the pre-2026-08-08 one-edit
  macro-promotion advice; it now states the two-edit rule, matching
  `shared/macros.tex` and the troubleshooting table.
- The template is self-contained again: a comment in `shared/macros.tex`
  and two example conventions referred to lectures and macros that the
  template does not ship.
- Stale or inconsistent references: the stage count in `WORKFLOW.md`; the
  `shared/`, `figures/`, and `drivers/` directory READMEs; `--strict` and
  `--no-pa11y` documented only in `--help`; `\alt` missing from the
  construct table; `setup.sh` missing from the layout table.

## 2026-08-08 — Revalidation fixes and hardening

An end-to-end revalidation — a fresh assistant started cold on a scanned
two-lecture source, with no instruction beyond "begin transcribing lecture
12" — produced a lecture matching an independently validated reference on
every content probe, and surfaced the fixes below.

### Fixed

- `./course.py slides` no longer hides overflowing frames. The build log is
  parsed **before** cleanup (it used to be deleted first, so the overfull
  check was silently vacuous): every run prints a box summary, any overfull
  box beyond a 2 pt sub-line tolerance fails the build with the log retained
  for diagnosis, and a missing log reports `boxes: NOT CHECKED` instead of
  passing. A green `slides NN` now means the deck **fits**, not merely that
  it compiled.
- Macro-promotion guidance corrected: promoting a lecture-local macro to
  `shared/macros.tex` is **two edits** — add the `\providecommand` there
  *and* delete the lecture's local definition. The shared file loads before
  every lecture body, so `\providecommand` does not protect a surviving
  local `\newcommand` (the old note claimed it did). The collision symptom
  has a troubleshooting row.

### Added

- `\sg{...}` (upright space-group symbols) in `shared/macros.tex`.
- Authoring rules learned by measurement, recorded in `conventions.md` and
  `docs/troubleshooting.md`: no `\genfrac`-stacked case labels and no
  incomplete math fragments — both drop out of parsed MathML (write "the
  eigenvalue $+1$ labels $\Gamma_1$", not `$+ \to \Gamma_1$`); character
  tables are real `tabular`s, never matrices; staged-reveal figures pin an
  identical `\useasboundingbox` across their states and select them with
  **open** overlay ranges, so the final figure survives the web flattening;
  `columns` reserves no trailing vertical space.

### Changed

- **S0 hardened:** the assistant asks for lecture boundaries before opening
  the source document at all — even a cheap text-layer probe. A self-found
  boundary presented for confirmation invites a rubber-stamp; the operator's
  own answer is the authority.
- **S3 waits for sign-off:** figure work begins only after the operator
  approves the S2 pass-2 draft, unless that review is explicitly waived.
- This changelog restructured as public release notes. The course-ledger
  seed stays in the header; the kit's full development ledger — every
  exploration and misstep — is preserved in git history.

## 2026-08-04 / 2026-08-05 — Post-release workflow round

### Added

- **S0 — source segmentation**, for courses that arrive as one continuous
  document instead of per-lecture files: the assistant asks the operator
  for the lecture boundaries (automatic detection is an explicit, costed
  opt-in), confirms them at interview before any transcription, and records
  each lecture's page range in its notes file.
- `source/` directory convention — `source/lectureNN.pdf`, untracked by
  git; when a file is missing, the assistant asks rather than hunting the
  filesystem.
- Optional conductor/worker guidance for tools that can delegate to
  subagents: the conductor owns shared files and every operator interview;
  workers stay lecture-local and propose.

### Changed

- The agent manual is **`AGENTS.md`** — the vendor-neutral convention;
  `CLAUDE.md` remains as a pointer stub for Claude-family tools.
- The human-side guide is **`WORKFLOW.md`**, at the repository root, so the
  top level tells the whole story (README · WORKFLOW.md · AGENTS.md) and
  `docs/` is the reference shelf. Human docs re-voiced: the assistant is
  the named subject of its own actions; "you" is reserved for what the
  reader actually does.
- Interview protocol tightened: every escalation arrives with a recommended
  resolution, never a bare question; batches open by re-reading
  `conventions.md` and the previous batch's notes; at close-out a lecture's
  notes condense to their durable record.

## 2026-08-04 — Initial release

Shipped as a GitHub **template repository**, MIT license.

- **One authored file per lecture, two targets, no transform:**
  `content/lectureNN.tex`, in an engine-neutral LaTeX subset, builds an
  accessible-HTML page (LaTeXML + BookML — native MathML, no JavaScript
  renderers, figures as SVG images; the primary target) and an optional
  beamer deck from the same source. The slide build doubles as a regression
  gate even for courses that never lecture from decks.
- **`./course.py`**, the one-command driver: `build`, `slides`, `check`,
  `figure` (fast standalone TikZ render-check), `index`, `doctor`, `clean`.
  Every web build runs the full gate suite: conversion-log triage,
  missing or empty alt text as build **errors**, a malformed-MathML
  counter, and a per-page accessibility audit (axe, via pa11y).
- **Alt text at birth:** every figure's description lives in an `alt/`
  sidecar written in the same session as the figure and wired into the
  HTML `<img alt>`.
- **The agent operating manual** and its binding contract — prose fidelity,
  step-for-step math ("show, don't tell"), calibrated flagging, append-only
  ledger discipline — with the staged S1–S4 workflow: operator interviews
  and validation gates at every stage boundary.
- **S5 — deck polish**, an optional author-driven round after the batch
  gate: the assistant flags candidates, the author picks, author-supplied
  narration goes in verbatim. The faithful S1–S4 output is a complete final
  state; skipping S5 is normal.
- **`setup.sh`** — idempotent, asks before installing anything, fetches
  BookML at a pinned, checksum-verified release; `./course.py doctor`
  audits the toolchain. Runs on a stock TeX Live: no version pinning.
- **Site styling:** a light CSS layer over BookML plain — reading column,
  frame cards, sticky page navigation, single forced-light scheme —
  accessibility-clean on every page.
- **Reference shelf** (`docs/`): setup details, the authoring subset and
  the reasons behind it, and a symptom → meaning → fix troubleshooting
  table distilled from real failures.
- Sidecar conventions: day-of-editable `announcements/` (slides-only, never
  in the published archive) and per-lecture `notes/` work records that make
  batches resumable by a fresh session.
- **Acceptance-tested end to end before shipping:** an isolated assistant,
  given only this repository's manual and thirteen pages of handwritten
  notes, re-authored a real lecture through the full workflow — interviews,
  figures, alt text, gates — and the result matched the course's
  independently validated version on every content check.
