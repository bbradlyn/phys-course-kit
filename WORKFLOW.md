# Workflow

Three loops at three timescales: transcription (per lecture batch), the
day-of-lecture minute, and publishing. The transcription loop is written as
executable instructions for your AI assistant in `AGENTS.md`; this page is
the human overview of the same process.

## Transcribing lectures (S0 → S5, in batches of 3–5)

One conditional step comes before everything: if your course arrives as a
single continuous document (a full semester of notes in one PDF) rather
than per-lecture files, the assistant will first ask you where the lecture
boundaries fall — **tell it** (your syllabus knows). It can detect them
instead, but only if you ask it to, and it will warn you first: scanning a
whole semester's document is expensive in assistant working memory, and
its coarse skim is a proposal for your confirmation either way.

Per lecture, four stages:

1. **S1 — triage.** The assistant reads the source material end to end and
   produces a page map, the topic arc, and an ambiguity list. **You answer
   the ambiguities before drafting starts** — unreadable passages, notation
   choices that will bind later lectures, scope calls. Answers that bind the
   future go straight into `conventions.md`.
2. **S2 — draft, two passes.** The assistant writes the full transcription
   into `content/lectureNN.tex` under the fidelity contract (your prose
   kept where it exists; derivations step for step). You review it slide by
   slide; the assistant applies your notes as pass 2 — pass 2 is your edit,
   nothing more.
3. **S3 — figures.** The assistant reconstructs every figure as TikZ,
   render-checks each one, and **writes the alt text in the same session**.
   You review the geometry and approve the descriptions.
4. **S4 — accessibility & polish.** The assistant adds progressive reveals
   where they help a live audience (conceptual chunks —
   intro/recap/takeaways frames stay static), fixes density, and runs the
   full gate suite on both targets.
5. **S5 — deck polish (optional).** S1–S4 delivers the faithful version,
   and stopping there is normal. If you want more craft — connecting
   sentences between results, thin slides merged, finer reveal pacing,
   text-beside-figure layouts — review the rendered PDF and hand the
   assistant your edits. Your added sentences go in verbatim (the
   no-inventing rule binds the assistant, not you), and they flow into the
   web page too, since there is one source. State the same preference twice
   and it becomes a convention the assistant applies automatically from
   then on. Gates re-run after.

Batch gate, before moving on: the assistant shows you `./course.py build NN`
green for every lecture in the batch (the check suite runs automatically)
and `slides NN` green, re-reads its transcription against the source on
both fidelity axes, and appends the batch's `CHANGELOG.md` row. **Your
part is the sign-off** — content and alt text, with the assistant's
fidelity self-review in front of you. Nothing proceeds past a batch you
haven't signed.

## The day of lecture

```
edit announcements/lectureNN.tex      # three bullets, thirty seconds
./course.py slides NN                 # fresh PDF, walk to class
```

Lecture bodies never change for day-of logistics; the published site never
sees announcements at all (a one-off `build NN --keep-announcements` exists
if you ever want a web copy with them).

## Publishing

```
./course.py build --all               # every lecture + the site index, gated
```

The site is the contents of `build/web/html/` — self-contained static files
(one directory per lecture + `index.html`), ready to copy to any static
host. The index is generated from the lecture titles in `content/` — there
is no separate table of lectures to maintain. **Before the first real
publish**: delete the sample lecture (`content/lecture00.tex`, its figure,
alt, and announcements files), or it will appear in the index alongside your
actual lectures.

## The regression stance

The slides target is a **gate, not just an output**: even if you never
lecture from decks, `./course.py slides NN` must stay green — it proves the
content still compiles under both drivers, i.e. nothing target-specific has
crept into the single source. The assistant runs it at every batch gate;
run it yourself after any hand edit.

## Ledger duties (what keeps the project recoverable)

- Every working session that changes content or process gets a row in
  `CHANGELOG.md` (append-only — never edit past rows). The assistant does
  this as part of its contract; when you edit by hand, the duty is yours.
- Decisions that bind future lectures get distilled into `conventions.md` —
  including taste: house terminology, table styles, pacing preferences. An
  unrecorded preference is one the assistant is *forbidden* to guess at.
- When a gate fires, `docs/troubleshooting.md` maps the symptom to its
  meaning and fix; if you learn a new failure mode, add a row there too.
