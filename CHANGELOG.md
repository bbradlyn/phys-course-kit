# Changelog

This file has two jobs.

**In this template repository** it is the kit's release notes: features and
fixes, newest first, below the rule.

**In a course built from the template** it becomes the course's ledger.
Delete the release notes and start your own table in their place:

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
