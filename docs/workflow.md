# Workflow

Three loops at three timescales: transcription (per lecture batch), the
day-of-lecture minute, and publishing. The transcription loop is written as
executable instructions for your AI assistant in `CLAUDE.md`; this page is
the human overview of the same process.

## Transcribing lectures (S1 → S4, in batches of 3–5)

Per lecture, four stages — the donor course ran all 26 lectures through this
staging and it held up:

1. **S1 — triage.** The assistant reads the source material end to end and
   produces a page map, the topic arc, and an ambiguity list. **You answer
   the ambiguities before drafting starts** — unreadable passages, notation
   choices that will bind later lectures, scope calls. Answers that bind the
   future go straight into `conventions.md`.
2. **S2 — draft, two passes.** Pass 1: the full transcription into
   `content/lectureNN.tex`, under the fidelity contract (your prose kept
   where it exists; derivations step for step). You review slide by slide;
   pass 2 applies your notes.
3. **S3 — figures.** Every figure reconstructed as TikZ, render-checked
   (`./course.py figure NN name` renders one figure standalone in seconds),
   **with alt text written in the same session**. You review geometry and
   approve the descriptions.
4. **S4 — accessibility & polish.** Progressive reveals where they help a
   live audience (conceptual chunks — intro/recap/takeaways frames stay
   static), density fixes, and the full gate suite on both targets.

Batch gate, before moving on: `./course.py build NN` green for every lecture
in the batch (the check suite runs automatically), `slides NN` green, your
sign-off on content and alt text, and a `CHANGELOG.md` row recording the
batch. The fidelity review — transcription against source on both the prose
and math axes — is part of that sign-off, not an extra.

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
crept into the single source. Run it as part of every batch gate.

## Ledger duties (what keeps the project recoverable)

- Every working session that changes content or process appends a row to
  `CHANGELOG.md` (append-only — never edit past rows).
- Decisions that bind future lectures get distilled into `conventions.md`.
- When a gate fires, `docs/troubleshooting.md` maps the symptom to its
  meaning and fix; if you learn a new failure mode, add a row there too.
