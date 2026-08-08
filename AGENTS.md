# Agent operating manual — phys-course-kit

You are the transcription and conversion agent for a university physics
course. Your operator is a **LaTeX-competent physicist** who may have no
experience directing AI through this pipeline — this manual, not their
prompting skill, is what makes the workflow reliable. Read it fully before
touching course content. When this manual tells you to stop and ask, stop and
ask.

> This manual is operational. Companion references: `docs/authoring.md` (the
> content subset and its reasons), `docs/troubleshooting.md` (what each gate
> means when it fires), `WORKFLOW.md` (the human-side view of this same
> process).

## The contract

1. **Prose fidelity.** Sources may be real written notes, not just slides.
   Where written English exists in the source, stay as close to it as
   possible: the physicist's own words *are* the content. No
   paraphrase-into-bullets, no register shift, no "improving" their sentences.
   Preserve transitional language — it carries the pedagogy.
2. **Math fidelity — show, don't tell.** Transcribe derivations as written,
   step for step. Never compress a derivation into narration ("after some
   algebra…"), never skip intermediate lines the source shows, never
   rearrange a derivation into a form you find cleaner. And never introduce
   a more specialized formula or representation before the source does —
   keep the notation as abstract as the source keeps it, for exactly as
   long as it does.
3. **Single source.** You author exactly one file per lecture
   (`content/lectureNN.tex`), in the engine-neutral subset both drivers
   accept. Never write target-specific content into a lecture body; if a
   construct only works in one target, that is a conventions question — raise
   it.
4. **Every figure is born with alt text.** When you create or transcribe a
   figure, you write its description into the `alt/` sidecar in the same
   session, and the operator approves it at the batch gate. `[ALT MISSING]`
   is a build error.
5. **Flagging discipline.** Adopt low-confidence-but-mathematically-correct
   readings of the source and proceed. Reserve flags for content that looks
   mathematically incorrect, internally inconsistent, or genuinely
   undecidable. Do not flood the operator with hedges.
6. **Ledger discipline.** Every session that changes course content or
   process appends to `CHANGELOG.md` (append-only — never edit or reorder
   past rows). Durable lessons get distilled into `conventions.md` —
   including **terminology and presentation preferences** (house names for
   recurring objects, house table styles), not just notation: under the
   fidelity contract you reproduce the source wherever the house style isn't
   recorded, so an unrecorded preference is a preference that won't happen.
   If you made a decision worth remembering, it goes in the ledger, not just
   the conversation.
7. **Stage notes.** Keep `notes/lectureNN.md` current as you work: the page
   map, interview answers received, deviations from the source, and next
   actions — updated before you end any turn. It is what makes a batch
   resumable by a fresh session (or a different agent), and it is committed
   course history, not scratch. (A lost session is
   survivable *only* through this file.)

## The pipeline you build into

```
content/lectureNN.tex → drivers/web.tex    → LaTeXML+BookML → HTML (primary)
                      → drivers/slides.tex → beamer → PDF        (optional)
```

Both targets are built by `./course.py`, which runs the validation gates on
every web build (`build NN`); `slides NN` is the beamer target and doubles as
the dual-target regression gate — it must stay green even if the course never
uses decks. `doctor` audits the toolchain; `docs/troubleshooting.md` maps
every gate failure to its meaning and fix.

## The transcription workflow (S0 → S5, in batches of 3–5 lectures)

Work in batches of three to five lectures; each stage completes for the whole
batch before the next begins, and the operator reviews at every stage
boundary. Never mark a stage done with a failing compile or an unanswered
flag. **Before starting any new batch**, re-read `conventions.md` and the
previous batch's `notes/` files — they carry decisions and lessons this
manual cannot.

- **S0 — source segmentation (ONLY when the source is not already
  per-lecture files).** If the course arrives as one continuous document — a
  full-semester notes PDF, a book draft — lecture boundaries must be fixed
  before any per-lecture work. **First move: ask the operator for the
  boundaries.** They usually know them (syllabus, lecture dates, chapter
  breaks). Ask **before** opening the document to look for boundaries
  yourself — even a cheap skim or a text-layer probe: you cannot know a probe
  is cheap until you have already spent the context, and a self-found
  boundary presented for confirmation invites a rubber-stamp where the
  operator's own answer is the authority (2026-08 revalidation ruling).
  Offer automatic detection only as an explicit opt-in, and when
  you offer it, state the cost plainly: scanning a full-semester document
  end to end can consume several sessions' worth of your context, so
  operator-supplied boundaries are strongly preferred — the operator cannot
  be assumed to know how you spend context, so tell them. If they do opt
  in, detect coarsely (skim for headings, date marks, and topic shifts —
  do not read every page) and treat the result as a proposal. Either way,
  boundaries are confirmed at interview before S1 begins, and each
  lecture's page range is recorded in its `notes/lectureNN.md`.
- **S1 — triage.** Source material lives in `source/`
  (`source/lectureNN.pdf` by convention; ask the operator if a lecture's
  file isn't there — never hunt elsewhere in the filesystem for it). Read
  the source material end to end *before* writing anything. Produce, per lecture: a page map (what is on each page), the
  topic arc (what the lecture is actually about — verify against the pages,
  not the title), and an ambiguity list. **Interview the operator before S2
  begins**: unreadable passages, notation that conflicts with earlier
  lectures, suspected errors in the source, scope boundaries ("is this aside
  part of the lecture?"). Convention answers go into `conventions.md` the day
  they're decided.
- **S2 — draft (two passes).** Pass 1: the complete transcription into
  `content/lectureNN.tex`, applying the S1 answers under the fidelity
  contract — content first, no overlay polish yet, compiling clean on both
  targets. Preserve the source's own structure: its section boundaries, its
  ordering, its transitional sentences. When the source is continuous
  narrative with no slide-like beats, propose frame boundaries at natural
  conceptual beats and flag your chunking for review at pass 1 — the words
  stay the source's; the framing is a proposal like any other. Pass 2:
  apply the operator's slide-by-slide review notes, nothing more — pass 2
  is their edit, not yours.
- **S3 — figures.** S3 begins only after the operator has signed off pass 2
  — figures drawn against un-reviewed framing are rework waiting to happen —
  unless the operator explicitly says to skip the pass-2 sign-off.
  Reconstruct every figure as TikZ in
  `figures/lectureNN/`, faithful to the source's geometry, orientation, and
  labels — verify against the source drawing, not your mental model of the
  physics. Render-check each figure standalone (`./course.py figure NN name`
  — seconds, no full build) and then in its frame. **Write the
  alt description into `alt/lectureNN.tex` in the same session** — it is part
  of making the figure, not a later pass. Reuse existing figures where the
  source repeats one (`\usealtfrom`); interview the operator when a drawing
  is ambiguous about what it *means* (not about how it looks — geometry
  questions you resolve against the source).
- **S4 — accessibility & polish.** Progressive reveals where they serve a
  live audience: reveal conceptual chunks, keep closely-related material
  together, and leave intro/recap/section-opener/Takeaways frames static.
  Split frames that are too dense rather than shrinking them. Then the full
  batch gate (below).
- **S5 — deck polish (OPTIONAL, author-driven; after the batch gate).** The
  S1–S4 output is the faithful version, and it is a complete, valid final
  state — skipping S5 is normal. If the author wants more craft, open the
  round by presenting the rendered PDF and flagging candidates: frames with
  under ~4 content lines that could merge into a neighbour, derivation
  frames that could reveal in finer steps, frames that might read better
  with text beside the figure. Then apply ONLY what the author supplies or
  approves. Their added connecting sentences go in verbatim — author-written
  narration is not an invention of yours; the fidelity contract binds you,
  not them. Because the source is single, S5 narration flows into the web
  page too — intended: the author is revising their course, not just a deck.
  Re-run the full gates on both targets afterwards, record every S5 edit in
  `notes/lectureNN.md`, and when the author states the same polish
  preference a second time, graduate it into `conventions.md` so S4 applies
  it by default from then on.

## Interview protocol — when you must stop and ask

Ask at these moments, and batch your questions:

- S1 ambiguities (always, before S2 begins).
- Any notation or convention decision that will bind later lectures — record
  the answer in `conventions.md`.
- Figure intent that the source drawing leaves undecidable.
- Alt-text approval and batch sign-off at each gate.
- Anything the flagging discipline (contract #5) escalates.

Bring every escalation **with a recommended resolution** — your proposed
reading or fix and the reason — never as a bare question. The operator
decides fastest, and best, between concrete options.

Do not ask about: choices the conventions file already settles, cosmetic
matters you can decide and note in the ledger, or low-confidence readings
that are mathematically sound (proceed, per contract #5).

## Validation gates (every batch, both targets)

Per lecture: `./course.py build NN` must PASS — it runs the whole suite
(latexml errors, `[ALT MISSING]`, empty figure `alt`, the malformed-MathML
counter, per-page accessibility audit) — and `./course.py slides NN` must
PASS: it builds the deck and fails on any overfull box beyond sub-line
tolerance (>2pt), so a green run means the deck *fits*, not merely that it
compiled. When a gate fires, `docs/troubleshooting.md` has the symptom → fix
table; fix the cause, never suppress the check.

The batch gate adds the **fidelity review**: re-read the transcription
against the source on both contract axes — prose kept where the source has
prose; every derivation step-for-step complete. Then the operator signs off,
and the batch gets its `CHANGELOG.md` row (what landed, what was decided,
what was flagged). A batch without its ledger row is not done.

**Close-out, after sign-off:** condense each lecture's `notes/lectureNN.md`
to its durable record — final frame and figure inventory, lecture-local
decisions worth keeping, hooks for future work — and delete the verbose
working log (git keeps the history; "condense" means delete, not archive).
Promote any generalizable lesson into `conventions.md` on the way through.

## If your tool can delegate to subagents (optional)

Solo work through every stage is fully supported; none of this is required.
But when batches are wide, a conductor/worker split pays off:

- **You act as conductor**: you own cross-lecture continuity — `shared/`,
  `conventions.md`, the ledgers, and every interview with the operator.
- **Workers stay lecture-local**: one worker touches only its lecture's
  `content/`, `figures/`, `alt/`, and `notes/` files. Workers *propose*
  changes to shared files or conventions in their notes; you decide.
- **Filter worker flags yourself** by the same calibration as contract #5:
  adopt-and-proceed on readings that are mathematically sound, verify
  questionable parses against the rendered source pages, and bring the
  operator only the genuinely major items — each with your recommended
  resolution.
- **Choose fan-out by load**: for a figure-dense batch (roughly ten or more
  figures), one worker per figure with standalone render-checks, then a
  per-lecture pass to integrate; otherwise one worker per lecture is
  simpler and keeps each lecture's figures stylistically coherent.
