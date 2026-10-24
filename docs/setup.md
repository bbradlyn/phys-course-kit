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
3. Run `./setup.sh`, then `./course.py build 00` (on Windows: the steps in
   the Windows section below, then `python course.py build 00`) — the sample
   lecture should print `PASS`, with every check passing. Then put your
   lecture sources in `source/` and hand the repository to your agentic AI
   tool ("Read AGENTS.md, then begin lecture 1 from source/lecture01.pdf" —
   or, if the whole course is one document, name that file and give the
   lecture boundaries) — your side of the loop is `WORKFLOW.md` at the
   repository root.

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

On macOS and Linux, `./setup.sh` checks all of it, asks before installing
anything, and fetches BookML at its fixed release (`--dry-run` shows what it
would do without changing anything; `--yes` answers yes to every install
prompt, for unattended runs); Windows has its own section below. **No
particular TeX version is needed**: the kit runs on a
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
  library is; if you set `LIBGS` yourself, your value is used instead. TeX
  Live's Windows `dvisvgm` has Ghostscript built in, so nothing is needed there.
- **BookML version**: pinned — that is, fixed at the top of `setup.sh` (a
  version number plus an sha256 checksum). To upgrade deliberately: change
  both, re-run `setup.sh`, rebuild everything, and record it in
  `CHANGELOG.md`. Never upgrade mid-semester without rebuilding and
  re-checking everything.
- **The browser the audit uses**: pa11y inspects a page by driving a real
  browser. On macOS, `course.py` points it at an installed
  Chrome/Chromium/Edge automatically (the copy pa11y would otherwise
  download for itself is unreliable on some machines); on Windows it lets
  pa11y use its own copy and retries with the installed Edge if that fails
  to launch; to choose a different browser, set `PUPPETEER_EXECUTABLE_PATH`
  to its path.
- **pa11y is optional by default**: without it, `build` and `check` still
  produce and check the page, skip the audit, and print a warning with
  install instructions (the audit needs Node.js, which not every machine
  or assistant can install). `--strict` turns a missing pa11y (or a browser that
  fails to launch) into a build failure — use it for automated runs on
  another machine; `--no-pa11y` skips the audit deliberately when you want
  a fast local rebuild.

## Windows

`setup.sh` is a macOS/Linux script; on Windows its steps are done by hand,
once, and `course.py` itself then runs there like anywhere else. Type the
commands in a PowerShell window (or Git Bash) opened in the repository
folder.

1. **TeX Live**, from the official installer (tug.org/texlive). Its
   `dvisvgm` already has Ghostscript built in, so nothing more is needed on
   that front.
2. **LaTeXML** needs a Perl, and Windows has none: install Strawberry Perl
   (`winget install StrawberryPerl.StrawberryPerl`), open a **new** terminal
   so that it is found, and run `cpanm --notest LaTeXML` (LaTeXML's test
   suite is slow and has Windows-only failures; the first `build 00`
   verifies the install instead). `UUID::Tiny` may be reported missing at
   the end — the build does not need it. Strawberry Perl also brings
   `gmake`, the GNU make that BookML is built on; `course.py` uses it when
   there is no `make`.
3. **BookML**: download the pinned `release.zip` from the BookML releases
   page (the version and its checksum are the two lines at the top of
   `setup.sh`) and unzip it in the repository folder so that
   `bookml/bookml.mk` exists — the zip already holds the `bookml/` folder.
4. **Node.js** from nodejs.org, then `npm install -g pa11y`. If PowerShell
   answers `npm` or `pa11y` with "running scripts is disabled on this
   system", run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once
   (or type `npm.cmd`); `course.py` is not affected either way.
5. **Python 3** (the python.org installer with "Add python.exe to PATH"
   ticked, or an Anaconda/Miniconda prompt). The driver is then
   `python course.py ...` wherever these pages say `./course.py ...`:
   `python course.py doctor` should report everything present, and
   `python course.py build 00` should print `PASS`.

What `course.py` does for you on Windows: it puts Strawberry Perl's folders
first on the PATH of every build command, so LaTeXML, `gmake` and the Perl
that can run LaTeXML are found even from Git Bash (whose own `perl` cannot
run it); set `KIT_STRAWBERRY` if Strawberry Perl lives somewhere other than
`C:\Strawberry`. It runs BookML's make with `cmd.exe` as its shell, which is
what BookML expects on Windows; it falls back to the installed Edge when
pa11y's own browser fails to launch; and it corrects the one backslash
`latexmlpost` writes into each page's stylesheet link.

## A container instead of installs

BookML publishes a container image with LaTeXML, BookML and a complete TeX
Live preinstalled, `ghcr.io/vlmantova/bookml` (with smaller `bookml-basic`,
`bookml-small` and `bookml-medium` images beside it). It is the
machine-independent fallback for a computer that cannot take the installs
above, with caveats: the bundled TeX Live is old (2021 at the time of
writing); the BookML inside it is the image's own copy, not the release
pinned in `setup.sh`; and only the BookML step runs inside it — `course.py`'s
checks, the slide build and the figure render-check run outside, on your own
machine, which still needs Python, pa11y and a TeX of its own. BookML's
documentation has the `docker run` invocation (it mounts the repository
folder into the container); `course.py check NN` then runs the checks on the
pages it produced.
