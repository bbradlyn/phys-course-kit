# Day-0 setup

Goal: from "Use this template" to a green `./course.py build 00` in one
sitting. Everything here is checked by `./course.py doctor`, so you always
know where you stand.

## Instantiating the template

1. On GitHub, press **Use this template** → create your course repository
   (clean history, no connection back to the kit).
2. Edit **`shared/course.tex`** — the one file holding course identity
   (code, title, term, URL). Nothing else needs renaming.
3. Run `./setup.sh`, then `./course.py build 00` — the sample lecture should
   PASS with all gates green. Then start transcribing `lecture01` (see
   `workflow.md` and, for your AI assistant, `CLAUDE.md`).

Optional: to receive later kit improvements, add the kit as a remote and
cherry-pick what you want:

```
git remote add kit-upstream https://github.com/OWNER/phys-course-kit
git fetch kit-upstream
```

## What the toolchain is

| Tool | Role | Install |
|---|---|---|
| TeX Live (full) | pdflatex, latexmk, dvisvgm, the `preview`/`comment` packages | MacTeX on macOS; `texlive-full` on Linux |
| LaTeXML 0.8.8+ | the LaTeX→XML→HTML engine | `brew install latexml` / distro package / `cpanm LaTeXML` |
| Ghostscript (with libgs) | dvisvgm reads figure baselines through the Ghostscript *library* | `brew install ghostscript` |
| BookML (pinned) | LaTeXML wrapper: dvisvgm figure images, packaging | fetched by `setup.sh`, checksum-verified |
| Node + pa11y (optional) | accessibility audits in the check suite | `npm install -g pa11y` |

`./setup.sh` checks all of it, asks before installing anything, and fetches
BookML at the pinned release (`--dry-run` to preview, `--yes` for CI-style
runs). **No TeX pinning is needed**: the kit runs on a current stock TeX Live
(validated on TL2026). If a machine ever does need a specific TeX, set
`KIT_TEXBIN=/path/to/texbin` — `course.py` prepends it everywhere.

## Notes and known wrinkles

- **libgs**: without the Ghostscript library, builds still succeed but each
  figure logs an image-depth error (baseline alignment only — harmless for
  display figures). `course.py check` knows the difference and says so. On
  macOS, `course.py` auto-points dvisvgm at a Homebrew `libgs.dylib` via the
  `LIBGS` environment variable; a user-set `LIBGS` always wins.
- **BookML version**: pinned (version + sha256) at the top of `setup.sh`.
  To upgrade deliberately: bump both pins, re-run `setup.sh`, rebuild
  everything, and record it in `CHANGELOG.md`. Never upgrade mid-semester
  without a full rebuild + check pass.
- **pa11y browser**: on macOS, `course.py` points pa11y's puppeteer at an
  installed Chrome/Chromium/Edge automatically (bundled-Chromium downloads
  are unreliable on some machines); `PUPPETEER_EXECUTABLE_PATH` overrides.
- **Windows**: `setup.sh` is POSIX. Manual equivalents: install TeX Live,
  LaTeXML (Strawberry Perl + cpanm), Ghostscript, Node; unzip the pinned
  BookML release into `bookml/`. Known gotcha: npm's
  global `.ps1` shims are blocked by PowerShell's default execution policy —
  `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` fixes pa11y.
