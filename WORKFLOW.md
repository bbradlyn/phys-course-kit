# Workflow

Three loops at three timescales: transcription (per lecture batch), the
day-of-lecture minute, and publishing. The transcription loop is written as
step-by-step instructions for your AI assistant in `AGENTS.md`; this page is
the human overview of the same process.

## Transcribing lectures (in batches of 3–5)

One conditional step comes before everything (the assistant's manual calls
it S0): if your course arrives as a
single continuous document (a full semester of notes in one PDF) rather
than per-lecture files, the assistant will first ask you where the lecture
boundaries fall — **tell it** (your syllabus knows). It can detect them
instead, but only if you ask it to, and it will warn you first: scanning a
whole semester's document is expensive in assistant working memory, and
its coarse skim is a proposal for your confirmation either way.

Per lecture, four stages — and a fifth only if you lecture from slides:

1. **S1 — triage.** The assistant reads the source material end to end and
   produces a page map, the topic arc, and an ambiguity list. **You answer
   the ambiguities before drafting starts** — unreadable passages, notation
   choices that will bind later lectures, scope calls. Answers that bind the
   future go straight into `conventions.md`.
2. **S2 — draft, two passes.** The assistant writes the full transcription
   into `content/lectureNN.tex` under the fidelity contract (your prose
   kept where it exists; derivations step for step). You review it slide by
   slide; the assistant applies your notes as pass 2 — pass 2 is your edit,
   nothing more. Figures wait for this: the assistant starts S3 only once
   you've signed off pass 2, unless you explicitly tell it to skip that
   review.
3. **S3 — figures.** The assistant reconstructs every figure as TikZ,
   render-checks each one, and **writes the alt text in the same session**.
   You review the geometry and approve the descriptions.
4. **S4 — checks and sign-off.** The assistant builds every lecture in the
   batch both ways and shows you the results: the web page with all its
   checks passing — no conversion errors, a description on every figure,
   well-formed math, and an automated accessibility audit of every page
   (if the audit software is missing, the build still produces the page
   and prints a warning with install instructions; the assistant shows you
   the warning, and you decide — install it, or sign off with the audit
   skipped) — and the slide
   version building cleanly (even if you never use it; see below). It
   re-reads its transcription against your source on both fidelity counts
   — your prose, your derivations. **Your part is the sign-off** — content
   and figure descriptions, with the assistant's fidelity self-review in
   front of you; then the assistant appends the batch's row to
   `CHANGELOG.md`. Nothing proceeds past a batch you haven't signed, and
   nothing after S4 is required: the signed batch is the finished lecture.
   (After sign-off the assistant condenses its working notes to a durable
   per-lecture record — the verbose logs live on in git.)
5. **S5 — slides (only if you lecture from them).** Say so once, by setting
   `\coursedecks` to `yes` in `shared/course.tex`; a course that lives on
   the web alone never enters this stage and never has to fit its frames
   onto slides. The assistant first adds progressive reveals by the
   standing rules (conceptual chunks; intro, recap, and takeaways frames
   stay static) and splits any frame that overflows a slide. Then, if you
   want more craft — connecting sentences between results, thin slides
   merged, finer reveal pacing, text beside a figure — review the PDF and
   hand the assistant your edits. Your added sentences go in verbatim (the
   no-inventing rule binds the assistant, not you), and they flow into the
   web page too, since there is one source; apart from that, and a new
   section heading wherever a frame was split to fit a slide, S5 leaves
   the web page as you signed it. State the same preference twice and it becomes a convention
   the assistant applies automatically from then on. The checks run again
   afterwards.

If your assistant's tool can delegate, it may hand lecture-local work to
helper instances; you still deal with one assistant, which owns every
question to you and every shared file.

## The day of lecture

If you lecture from slides:

```
edit announcements/lectureNN.tex      # three bullets, thirty seconds
./course.py slides NN                 # fresh PDF, walk to class
```

Lecture bodies never change for day-of logistics; the published site never
sees announcements at all (a one-off `build NN --keep-announcements` exists
if you ever want a web copy with them).

## Publishing

```
./course.py build --all               # every lecture + the site index, checked
```

The site is the contents of `build/web/html/` — self-contained plain files
(one directory per lecture + `index.html`), ready to copy to any web host
that serves plain files. The index is generated from the lecture titles in
`content/` — there is no separate table of lectures to maintain
(`./course.py index` regenerates the index alone). **Before
the first real publish**: delete the sample lecture
(`content/lecture00.tex`, its figure, alt, and announcements files), or it
will appear in the index alongside your actual lectures.

## Why the slide version is always built

Every lecture is built as slides as well as a web page, even in a course
that never uses them, because one source feeds both: if the slide build
breaks, something has crept into a lecture that only one of the two
understands, and the assistant fixes it before you sign. Only a course
that lectures from slides (`\coursedecks` set to `yes`) is also held to
every frame fitting on its slide; for everyone else the slide build is a
check that costs you nothing. After any edit you make by hand, run
`./course.py build NN` and `./course.py slides NN` yourself.

## Ledger duties (what keeps the project recoverable)

- Every working session that changes content or process gets a row in
  `CHANGELOG.md` (append-only — never edit past rows). The assistant does
  this as part of its contract; when you edit by hand, the duty is yours.
- Decisions that bind future lectures get distilled into `conventions.md` —
  including taste: house terminology, table styles, pacing preferences. An
  unrecorded preference is one the assistant is *forbidden* to guess at.
- When a check fails, `docs/troubleshooting.md` maps the symptom to its
  meaning and fix; if you learn a new failure mode, add a row there too.
