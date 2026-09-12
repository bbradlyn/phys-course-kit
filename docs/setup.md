# Day-0 setup

Goal: from "Use this template" to a `./course.py build 00` that passes, in
one sitting. `./course.py doctor` checks the installed software for you, so you
always know where you stand.

## Making your course from the template

1. On GitHub, press **Use this template** → create your course repository
   (clean history, no connection back to the kit).
2. Edit **`shared/course.tex`** — the one file holding course identity
   (code, title, term, URL) and whether you lecture from slides
   (`\coursedecks`, `no` unless you say otherwise). Nothing else needs
   renaming.
3. Run `./setup.sh`, then `./course.py build 00` — the sample lecture should
   print `PASS`, with every check passing. Then put your lecture sources in
   `source/` and hand the repository to your agentic AI tool ("Read
   AGENTS.md, then begin lecture 1 from source/lecture01.pdf" — or, if the
   whole course is one document, name that file and give the lecture
   boundaries) — your side of the loop is `WORKFLOW.md` at the repository
   root.

Optional: to receive later kit improvements, add the kit as a second remote
and take just the changes you want:

```
git remote add kit-upstream https://github.com/bbradlyn/phys-course-kit
git fetch kit-upstream
```

## The software the kit needs

| Tool | Role | Install |
|---|---|---|
| TeX Live (full) | pdflatex, latexmk, dvisvgm, the `preview`/`comment` packages | MacTeX on macOS; `texlive-full` on Linux |
| LaTeXML 0.8.8+ | the LaTeX→XML→HTML engine | `brew install latexml` / distro package / `cpanm LaTeXML` |
| Ghostscript (with libgs) — recommended; without it builds still pass, with a harmless warning about figure baselines | dvisvgm reads figure baselines through the Ghostscript *library* | `brew install ghostscript` |
| BookML (one fixed version) | a layer on top of LaTeXML: dvisvgm figure images, packaging | fetched by `setup.sh`, checksum-verified |
| Node (the JavaScript runtime pa11y runs on) + pa11y — needed for the accessibility audit; without it the build still produces the page and prints a warning with install instructions | the accessibility audit among the checks | `npm install -g pa11y` |

`./setup.sh` checks all of it, asks before installing anything, and fetches
BookML at its fixed release (`--dry-run` shows what it would do without
changing anything; `--yes` answers yes to every install prompt, for
unattended runs). **No particular TeX version is needed**: the kit runs on a
current stock TeX Live (validated on TL2026). If a machine ever does need a
specific TeX, set `KIT_TEXBIN=/path/to/texbin` — the directory holding that
TeX's programs — and `course.py` looks there first for every command it
runs.

## Notes and known wrinkles

- **libgs**: without the Ghostscript library, builds still succeed but each
  figure logs an image-depth error (baseline alignment only — harmless for
  display figures). `course.py check` knows the difference and says so. On
  macOS, `course.py` points dvisvgm at a Homebrew `libgs.dylib` for you, by
  setting the `LIBGS` environment variable that tells dvisvgm where that
  library is; if you set `LIBGS` yourself, your value is used instead.
- **BookML version**: pinned — that is, fixed at the top of `setup.sh` (a
  version number plus an sha256 checksum). To upgrade deliberately: change
  both, re-run `setup.sh`, rebuild everything, and record it in
  `CHANGELOG.md`. Never upgrade mid-semester without rebuilding and
  re-checking everything.
- **The browser the audit uses**: pa11y inspects a page by driving a real
  browser. On macOS, `course.py` points it at an installed
  Chrome/Chromium/Edge automatically (the copy pa11y would otherwise
  download for itself is unreliable on some machines); to choose a
  different browser, set `PUPPETEER_EXECUTABLE_PATH` to its path.
- **pa11y is optional by default**: without it, `build` and `check` still
  produce and check the page, skip the audit, and print a warning with
  install instructions (the audit needs Node.js, which not every machine
  or assistant can install). `--strict` turns a missing pa11y (or a browser that
  fails to launch) into a build failure — use it for automated runs on
  another machine; `--no-pa11y` skips the audit deliberately when you want
  a fast local rebuild.
- **Windows**: `setup.sh` is written for macOS and Linux. Do the same steps
  by hand: install TeX Live, LaTeXML (Strawberry Perl + cpanm),
  Ghostscript, Node; unzip the fixed BookML release into `bookml/`. Known
  gotcha: npm's global `.ps1` shims are blocked by PowerShell's default
  execution policy — `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
  fixes pa11y.
