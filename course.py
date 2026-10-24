#!/usr/bin/env python3
"""course.py — one-command driver for the course (phys-course-kit).

Verbs:
  build NN | --all [--keep-announcements] [--no-pa11y | --strict]
      Web target (PRIMARY): generate the root build file, run the BookML build,
      then the full check suite on the result.
  slides NN | --all
      Beamer PDF into build/slides/ (announcements sidecars always included —
      that is their point).  Also the check that the single source still
      builds both ways; when shared/course.tex sets \\coursedecks to yes it
      additionally fails on any overfull frame (slide fit).
  check NN | --all [--no-pa11y | --strict]
      Check suite only, on existing web builds.
  figure NN name
      Render one TikZ figure standalone (build/figures/lectureNN-name.pdf,
      plus .png on macOS) — the fast S3 render-check loop.
  index
      Generate the site index (build/web/html/index.html) from the lecture
      titles scraped out of content/ — no separate manifest to maintain.
  doctor
      Report on the software the kit needs and on the course as configured.
  clean [--deep]
      Remove build outputs and generated wrappers; --deep also drops the
      bmlimages figure cache (forces re-rendering).

Lecture names are forgiving: 5, 05, lecture05 all work.

Software: a full TeX Live plus latexml, both runnable from your terminal, is
all that is expected — no particular TeX version (verified: the kit runs on
stock TeX Live 2026).
Set KIT_TEXBIN to prepend a specific TeX bin directory if you need one.
On Windows, which has no system Perl, LaTeXML lives in Strawberry Perl
(C:\\Strawberry, or KIT_STRAWBERRY): its directories go first on PATH for
every build command and its gmake stands in for make; run the driver as
`python course.py ...` (docs/setup.md has the install recipe).
"""

import argparse
import glob
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

# Console output goes through UTF-8 whatever the console's code page (a pa11y
# or LaTeXML message carrying a math glyph would otherwise crash a redirected
# stdout under Windows' cp1252 mid-batch) and is line-buffered, so a
# redirected `build --all` log shows progress; harmless on a UTF-8 terminal.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
BUILD = ROOT / "build"
WEB_AUX = BUILD / "web"          # BookML AUX_DIR (set in GNUmakefile)
SITE = WEB_AUX / "html"          # built pages: SITE/lectureNN/index.html
SLIDES = BUILD / "slides"
BOOKML = ROOT / "bookml"


# ---------------------------------------------------------------------------
# environment
# ---------------------------------------------------------------------------

def strawberry_root(env):
    """Windows only: Strawberry Perl's folder (KIT_STRAWBERRY, else
    C:\\Strawberry), where LaTeXML and gmake live; None when absent."""
    for cand in (env.get("KIT_STRAWBERRY"), r"C:\Strawberry"):
        if cand and (Path(cand) / "perl" / "bin" / "perl.exe").is_file():
            return Path(cand)
    return None


def base_env():
    env = os.environ.copy()
    pre = []
    texbin = env.get("KIT_TEXBIN")
    if texbin:
        pre.append(texbin)
    if sys.platform == "win32":
        # Windows has no system Perl: latexml.bat, the Perl with XML::LibXML
        # and gmake all live in Strawberry Perl, whose directories are not
        # always on PATH (and Git Bash's own perl shadows them when they are).
        sb = strawberry_root(env)
        if sb:
            pre += [str(sb / "perl" / "site" / "bin"), str(sb / "perl" / "bin"),
                    str(sb / "c" / "bin")]
    if pre:
        env["PATH"] = os.pathsep.join(pre + [env.get("PATH", "")])
    # dvisvgm needs the Ghostscript LIBRARY to read preview baseline specials
    # (BookML image depths); point it at a Homebrew/system libgs when the
    # environment hasn't already (a user-set LIBGS always wins).  TeX Live's
    # Windows dvisvgm carries its own Ghostscript.
    if sys.platform == "darwin" and not env.get("LIBGS"):
        for cand in ("/opt/homebrew/lib/libgs.dylib", "/usr/local/lib/libgs.dylib"):
            if Path(cand).exists():
                env["LIBGS"] = cand
                break
    return env


def which(name, env=None):
    """The program as found on the build PATH (base_env's, not the shell's)."""
    return shutil.which(name, path=(env or base_env()).get("PATH"))


def make_exe(env):
    """GNU make -- or gmake / mingw32-make, the names it goes by where there
    is no `make` (Strawberry Perl and MinGW ship it so on Windows)."""
    for name in ("make", "gmake", "mingw32-make"):
        exe = which(name, env)
        if exe:
            return exe
    return None


def make_cmd(make, target):
    cmd = [make, target]
    if sys.platform == "win32":
        # GNU make on Windows runs its $(shell) probes through Git Bash's
        # sh.exe whenever that is on PATH, whatever SHELL the environment
        # says, and BookML's early `2>NUL` probes then leave a stray file
        # named NUL in the repository.  A SHELL given on the command line
        # applies before the makefile is read and reaches BookML's sub-make.
        cmd.append("SHELL=cmd.exe")
    return cmd


MAC_BROWSERS = ("Google Chrome.app/Contents/MacOS/Google Chrome",
                "Chromium.app/Contents/MacOS/Chromium",
                "Microsoft Edge.app/Contents/MacOS/Microsoft Edge")
WINDOWS_BROWSERS = (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe")


def system_browser():
    """An installed browser pa11y can drive: Chrome/Chromium/Edge on macOS,
    Edge (shipped with Windows) on Windows; None elsewhere."""
    if sys.platform == "darwin":
        cands = [Path("/Applications") / app for app in MAC_BROWSERS]
    elif sys.platform == "win32":
        cands = [Path(p) for p in WINDOWS_BROWSERS]
    else:
        cands = []
    for cand in cands:
        if cand.exists():
            return str(cand)
    return None


def pa11y_env(force_browser=False):
    """pa11y drives a real browser through puppeteer.  On macOS, point it at
    a system browser unless the user already did (bundled-Chromium downloads
    are unreliable on some machines); on Windows the bundled browser is
    tried first and the installed Edge only on the retry after a launch
    failure (force_browser).  A user-set PUPPETEER_EXECUTABLE_PATH always wins."""
    env = base_env()
    if not env.get("PUPPETEER_EXECUTABLE_PATH") and (sys.platform == "darwin" or force_browser):
        browser = system_browser()
        if browser:
            env["PUPPETEER_EXECUTABLE_PATH"] = browser
    return env


def run(cmd, env=None, cwd=ROOT, timeout=1800):
    env = env or base_env()
    # Resolve the program against the build PATH ourselves: Windows'
    # CreateProcess searches the parent's PATH, not the child's, and never
    # finds a .bat/.cmd (latexml, pa11y) given without its suffix.
    exe = shutil.which(cmd[0], path=env.get("PATH"))
    if exe:
        cmd = [exe] + list(cmd[1:])
    # Tool output is UTF-8 (LaTeXML, pa11y) whatever the console's code page.
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


# ---------------------------------------------------------------------------
# course + lecture metadata (all scraped from the sources: no manifest)
# ---------------------------------------------------------------------------

def course_meta():
    meta = {}
    text = (ROOT / "shared" / "course.tex").read_text(encoding="utf-8")
    for m in re.finditer(r"\\newcommand\{\\(course\w+)\}\{([^}]*)\}", text):
        meta[m.group(1)] = m.group(2)
    return meta


def course_decks():
    """True only when shared/course.tex sets \\coursedecks to yes: the course
    lectures from slides, so slide fit is enforced and S5 exists."""
    return course_meta().get("coursedecks", "no").strip().lower() == "yes"


def lectures():
    return sorted(p.stem[len("lecture"):]
                  for p in CONTENT.glob("lecture[0-9][0-9].tex"))


def norm_lecture(arg):
    m = re.fullmatch(r"(?:lecture)?(\d{1,2})", arg.strip())
    if not m:
        sys.exit(f"cannot parse lecture name: {arg!r}")
    nn = f"{int(m.group(1)):02d}"
    if not (CONTENT / f"lecture{nn}.tex").exists():
        sys.exit(f"no such lecture: content/lecture{nn}.tex")
    return nn


def lecture_title(nn):
    text = (CONTENT / f"lecture{nn}.tex").read_text(encoding="utf-8")
    m = re.search(r"\\kitlecturetitle\{((?:[^{}]|\{[^{}]*\})*)\}", text)
    return " ".join(m.group(1).split()) if m else f"Lecture {int(nn)}"  # a title wrapped over lines stays one line


# ---------------------------------------------------------------------------
# web build (BookML)
# ---------------------------------------------------------------------------

def write_wrapper(nn, keep_announcements=False):
    """Root-level lectureNN.tex wrapper for BookML.  Written only when the
    content differs, so make's dependency caching keeps working."""
    lines = ["%% GENERATED by course.py -- do not edit, do not commit",
             r"\def\kitlecture{" + nn + "}"]
    if keep_announcements:
        lines.append(r"\def\kitkeepannouncements{}")
    lines.append(r"\input{drivers/web.tex}")
    want = "\n".join(lines) + "\n"
    path = ROOT / f"lecture{nn}.tex"
    if not path.exists() or path.read_text(encoding="utf-8") != want:
        path.write_text(want, encoding="utf-8")
    return path


def build_web(nn, keep_announcements=False):
    if not BOOKML.is_dir():
        sys.exit("bookml/ is missing -- run ./setup.sh to fetch it, or on Windows unzip "
                 "the pinned release into bookml/ (docs/setup.md)")
    env = base_env()
    make = make_exe(env)
    if not make:
        sys.exit("GNU make not found (make / gmake) -- on Windows, Strawberry Perl "
                 "provides gmake (docs/setup.md)")
    write_wrapper(nn, keep_announcements)
    # the target must match BookML's rules with forward slashes on Windows too
    target = f"{WEB_AUX.relative_to(ROOT).as_posix()}/html/lecture{nn}/index.html"
    print(f"  bookml: {Path(make).stem} {target}")
    rc, out = run(make_cmd(make, target), env=env)
    (BUILD / "logs").mkdir(parents=True, exist_ok=True)
    (BUILD / "logs" / f"lecture{nn}.make.log").write_text(out, encoding="utf-8")
    if rc != 0:
        print(out[-2000:])
        print(f"BUILD FAILED (make exit {rc}) -- full log: build/logs/lecture{nn}.make.log")
        return False
    postprocess(nn)
    return True


def postprocess(nn):
    """The post-build pass over a lecture's pages: the current stylesheet,
    table scroll wrappers, forward-slash hrefs.  Idempotent, and run by every
    `build` -- including one whose page make found up to date."""
    page_dir = SITE / f"lecture{nn}"
    sync_site_css(page_dir)
    wrap_tables(page_dir)
    fix_backslash_hrefs(page_dir)


def sync_site_css(page_dir):
    """Refresh the site stylesheet(s) in a built lecture.  latexmlpost copies
    them only when it runs, and a stylesheet edit does not make the page
    stale for make -- so `build` on an up-to-date lecture still delivers the
    current CSS."""
    dest = page_dir / "shared"
    if dest.is_dir():
        for src in (ROOT / "shared").glob("*.css"):
            if (dest / src.name).is_file():
                shutil.copyfile(src, dest / src.name)


def wrap_tables(page_dir):
    """Wrap every data table (<table class="ltx_tabular ...">) in
    <div class="table-scroll">, the narrow-screen scroll box shared/kit.css
    styles.  A wrapper rather than CSS on the table: display:block on a
    <table> strips its table semantics for screen readers in Chrome and
    Safari.  Nested tables are left alone; already-wrapped ones are skipped."""
    for page in sorted(page_dir.glob("*.html")):
        html = page.read_text(encoding="utf-8")
        out, pos, changed = [], 0, False
        for m in re.finditer(r'<table\b[^>]*class="[^"]*\bltx_tabular\b[^"]*"[^>]*>', html):
            if m.start() < pos:
                continue
            if html[max(0, m.start() - 40):m.start()].rstrip().endswith('<div class="table-scroll">'):
                continue
            depth, end = 0, None   # the matching </table>, honoring nesting
            for t in re.finditer(r"<table\b|</table>", html[m.start():]):
                depth += 1 if t.group(0) == "<table" else -1
                if depth == 0:
                    end = m.start() + t.end()
                    break
            if end is None or html.count("<table", m.start(), end) > 1:
                continue   # unterminated or nested: leave it
            out.append(html[pos:m.start()])
            out.append('<div class="table-scroll">' + html[m.start():end] + "</div>")
            pos, changed = end, True
        if changed:
            out.append(html[pos:])
            page.write_text("".join(out), encoding="utf-8")


def fix_backslash_hrefs(page_dir):
    """latexmlpost on Windows writes the copied --css path into every page
    with a backslash (href="shared\\kit.css"); forward slashes work on every
    platform.  Rewrites only what it finds -- a no-op on macOS and Linux."""
    for page in sorted(page_dir.glob("*.html")):
        html = page.read_text(encoding="utf-8")
        fixed = re.sub(r'href="([^"]*\\[^"]*)"',
                       lambda m: 'href="' + m.group(1).replace("\\", "/") + '"', html)
        if fixed != html:
            page.write_text(fixed, encoding="utf-8")


# ---------------------------------------------------------------------------
# slides build (latexmk)
# ---------------------------------------------------------------------------

# Sub-line bottom-margin tightness; anything larger clips content.  (An
# 18.6pt clipped frame once hid behind four "green" builds: latexmk -c had
# deleted the log before anyone could grep it, so the overfull check was
# silently vacuous.  The log is therefore parsed BEFORE cleanup.)
OVERFULL_TOLERANCE_PT = 2.0


def check_boxes(log_path):
    """Parse a retained latexmk .log for box warnings.

    Returns (over, under, bad): sizes (pt) of every Overfull box, the count of
    Underfull warnings, and the raw log lines of Overfull boxes larger than
    OVERFULL_TOLERANCE_PT (the ones that fail the gate)."""
    over, under, bad = [], 0, []
    for line in log_path.read_text(errors="replace").splitlines():
        if line.startswith("Underfull \\"):
            under += 1
        elif line.startswith("Overfull \\"):
            m = re.search(r"\(([0-9.]+)pt", line)
            pts = float(m.group(1)) if m else 0.0
            over.append(pts)
            if pts > OVERFULL_TOLERANCE_PT:
                bad.append(line.strip())
    return over, under, bad


def build_slides(nn):
    SLIDES.mkdir(parents=True, exist_ok=True)
    job = f"lecture{nn}-slides"
    outdir = SLIDES.relative_to(ROOT).as_posix()  # forward slashes on Windows too
    cmd = ["latexmk", "-pdf", f"-usepretex=\\def\\kitlecture{{{nn}}}",
           f"-jobname={job}", f"-output-directory={outdir}",
           "-interaction=nonstopmode", "-halt-on-error", "drivers/slides.tex"]
    rc, out = run(cmd)
    if rc != 0:
        print(out[-1500:])
        print(f"SLIDES FAILED (latexmk exit {rc})")
        return False
    log = SLIDES / (job + ".log")
    if not log.exists():
        # A silent skip must never read as a pass (the lesson this check
        # exists to encode).  rc==0 with no log means latexmk did no work.
        print(f"  boxes: NOT CHECKED -- no log at build/slides/{job}.log "
              "(latexmk skipped the build?); ./course.py clean, then rebuild")
        over, under, bad = [], 0, []
    else:
        over, under, bad = check_boxes(log)
        if over or under:
            detail = f"{len(over)} overfull (worst {max(over):.1f}pt)" if over \
                else "0 overfull"
            print(f"  boxes: {detail}, {under} underfull"
                  + ("" if bad else " -- within tolerance"))
        else:
            print("  boxes: clean")
    if bad:
        for line in bad[:10]:
            print(f"    {line}")
        if course_decks():
            print(f"SLIDES FAILED (overfull > {OVERFULL_TOLERANCE_PT:g}pt -- "
                  f"content may be clipped; log retained: build/slides/{job}.log)")
            return False
        print(f"  boxes: {len(bad)} overfull > {OVERFULL_TOLERANCE_PT:g}pt -- "
              "reported, not enforced (\\coursedecks is not yes: web-only course)")
    run(["latexmk", "-c", f"-jobname={job}",
         f"-output-directory={outdir}", "drivers/slides.tex"])
    for ext in (".nav", ".snm", ".vrb"):  # beamer extras latexmk -c leaves
        p = SLIDES / (job + ext)
        if p.exists():
            p.unlink()
    print(f"  slides OK -> build/slides/{job}.pdf")
    return True


# ---------------------------------------------------------------------------
# single-figure render check (the S3 inner loop)
# ---------------------------------------------------------------------------

def render_figure(nn, name):
    src = ROOT / "figures" / f"lecture{nn}" / f"{name}.tex"
    if not src.exists():
        sys.exit(f"no such figure: {src.relative_to(ROOT).as_posix()}")
    outdir = BUILD / "figures"
    outdir.mkdir(parents=True, exist_ok=True)
    job = f"lecture{nn}-{name}"
    wrapper = outdir / f"{job}.wrapper.tex"
    wrapper.write_text(
        "\\documentclass[margin=2mm]{standalone}\n"
        "\\usepackage{amsmath,amssymb,mathtools}\n"
        "\\usepackage{xcolor}\n"
        "\\usepackage{tikz}\n"
        "\\usetikzlibrary{arrows.meta,calc,positioning,shapes.geometric}\n"
        "\\tikzset{visible on/.style={}}\n"
        "\\input{shared/palette.tex}\n"
        "\\input{shared/macros.tex}\n"
        f"\\begin{{document}}\\input{{figures/lecture{nn}/{name}.tex}}\\end{{document}}\n",
        encoding="utf-8")
    rc, out = run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                   f"-output-directory={outdir.relative_to(ROOT).as_posix()}",
                   f"-jobname={job}", wrapper.relative_to(ROOT).as_posix()], timeout=300)
    if rc != 0:
        print(out[-1200:])
        print(f"FIGURE FAILED: {src.relative_to(ROOT).as_posix()}")
        return False
    pdf = outdir / f"{job}.pdf"
    print(f"  ok -> {pdf.relative_to(ROOT).as_posix()}")
    if sys.platform == "darwin":
        png = outdir / f"{job}.png"
        rc2, _ = run(["sips", "-s", "format", "png", str(pdf), "--out", str(png)],
                     timeout=120)
        if rc2 == 0:
            print(f"  ok -> {png.relative_to(ROOT).as_posix()}")
    for ext in (".aux", ".log", ".wrapper.tex"):
        p = outdir / (job + ext) if ext != ".wrapper.tex" else wrapper
        if p.exists():
            p.unlink()
    return True


# ---------------------------------------------------------------------------
# check suite
# ---------------------------------------------------------------------------

MATHML_TOKENS = {"mi", "mo", "mn", "mtext", "ms", "mspace",
                 "annotation", "annotation-xml"}


class _MathScan(HTMLParser):
    """Character data directly inside a non-token MathML element — the
    malformed-MathML signature (a standing tripwire)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.in_math, self.bare = [], 0, []

    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)
        if tag == "math":
            self.in_math += 1

    def handle_endtag(self, tag):
        while self.stack:
            if self.stack.pop() == tag:
                break
        if tag == "math":
            self.in_math = max(0, self.in_math - 1)

    def handle_data(self, data):
        if self.in_math and data.strip():
            parent = self.stack[-1] if self.stack else "?"
            if parent not in MATHML_TOKENS:
                self.bare.append((parent, data.strip()[:40]))


def bare_math_text(html_text):
    s = _MathScan()
    s.feed(html_text)
    return s.bare


# An overlay spec that reached the page as text: LaTeXML prints a text-mode
# "<2->" as "¡2-¿" (the OT1 glyphs), or escapes it literally.  Either means a
# construct's overlay argument was not stripped on the web -- a kit shim bug,
# never a content problem to paper over.
OVERLAY_LEAK_RE = re.compile(r"¡\d+(?:-\d*)?¿|&lt;\d+(?:-\d*)?&gt;")


def overlay_leaks(html_text):
    return OVERLAY_LEAK_RE.findall(html_text)


def libgs_available():
    rc, out = run(["dvisvgm", "-V1"], timeout=60)
    return rc == 0 and "Ghostscript" in out


def pa11y_page(path, strict, skip):
    if skip:
        return True, "skipped"
    exe = which("pa11y")
    if not exe:
        if strict:
            return False, "pa11y NOT INSTALLED (required by --strict)"
        return True, "not installed -- audit skipped; install Node.js, then `npm install -g pa11y`"
    cmd = [exe, "--runner", "axe", "--hide-elements", "math", path.resolve().as_uri()]
    env = pa11y_env()
    rc, out = run(cmd, env=env, timeout=300)
    if rc not in (0, 2):
        # exit 1 is a technical failure, typically puppeteer's bundled browser
        # not launching: retry once with the installed browser (Edge on
        # Windows) when that would change anything
        retry = pa11y_env(force_browser=True)
        if retry.get("PUPPETEER_EXECUTABLE_PATH") != env.get("PUPPETEER_EXECUTABLE_PATH"):
            rc, out = run(cmd, env=retry, timeout=300)
    if rc == 0:
        return True, "No issues found"
    if rc == 2:
        return False, "ACCESSIBILITY ISSUES:\n" + out[-1200:]
    return (not strict), f"TECHNICAL FAILURE (exit {rc}) -- browser/launch problem, not an audit result"


# ---------------------------------------------------------------------------
# widths at the normal column (desktop-first calibration)
# ---------------------------------------------------------------------------

# The reading column is capped at 46rem (shared/kit.css), so every viewport
# from about 800px up gives the same layout: that is the NORMAL width the site
# is calibrated for.  There, every display equation's ink and every data
# table must stay within this fraction of its card's inner width -- the rest
# is slack for browser math fonts, which differ by a few percent.  Wider
# means the SOURCE is fixed (break the equation, re-lay the table), never
# scrolled or scaled.  Below the normal width (phones, small tablets) an
# equation or table wider than the column scrolls within its own box
# (shared/kit.css), so the page never scrolls sideways; those boxes never
# engage at the normal width, which is what this check guarantees.
EQN_WIDTH_MAX = 0.90
EQN_VIEWPORT = "1280x1024"
EQWIDTH_JS = ROOT / "shared" / "eqwidth.js"


def npm_global_root(env):
    """Where `npm install -g` puts packages (pa11y, and its puppeteer)."""
    npm = which("npm", env)
    if not npm:
        return None
    rc, out = run([npm, "root", "-g"], env=env, timeout=60)
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    return lines[-1] if rc == 0 and lines else None


def puppeteer_dir(env):
    """pa11y's own node_modules, when Node and pa11y's puppeteer are there."""
    root = npm_global_root(env) if which("node", env) else None
    pup = Path(root) / "pa11y" / "node_modules" if root else None
    return pup if pup and (pup / "puppeteer").is_dir() else None


def equation_widths(pages, strict):
    """Run shared/eqwidth.js on the pages at the normal column.  Returns
    (ok, measured, lines): measured is False when the check could not run
    (no Node, no puppeteer, a browser failure) -- a warning, or a failure
    under --strict."""
    env = pa11y_env()
    pup = puppeteer_dir(env)
    if not pup:
        return (not strict), False, ["widths: NOT MEASURED -- needs Node.js and pa11y (its puppeteer "
                                     "drives the browser); equations and tables were not checked "
                                     "against the column"]
    node_path = str(pup) + os.pathsep + str(pup.parent.parent)
    env["NODE_PATH"] = node_path
    cmd = [which("node", env), str(EQWIDTH_JS), "--threshold", str(EQN_WIDTH_MAX),
           "--viewport", EQN_VIEWPORT, *[p.resolve().as_uri() for p in pages]]
    rc, out = run(cmd, env=env, timeout=900)
    if rc not in (0, 2):
        # a launch failure: retry once with the installed browser, as pa11y does
        retry = pa11y_env(force_browser=True)
        if retry.get("PUPPETEER_EXECUTABLE_PATH") != env.get("PUPPETEER_EXECUTABLE_PATH"):
            retry["NODE_PATH"] = node_path
            rc, out = run(cmd, env=retry, timeout=900)
    if rc not in (0, 2):
        return (not strict), False, ["widths: TECHNICAL FAILURE (browser launch?) -- not a measurement: "
                                     + " | ".join(out.strip().splitlines()[-3:])]
    data = json.loads([l for l in out.splitlines() if l.startswith("{")][-1])
    mx, mt = data.get("max") or {}, data.get("maxTable") or {}
    line = (f"widths at the normal column: {data['equations']} equations, widest "
            f"{round(100 * mx.get('ratio', 0))}% of the card"
            + (f" ({mx['page']}: {mx['alt'][:36]})" if mx else ""))
    if data.get("tables"):
        line += f"; {data['tables']} tables, widest {round(100 * mt.get('ratio', 0))}%"
    lines = [line]
    for x in data["over"][:8]:
        lines.append(f"  TOO WIDE {round(100 * x['ratio'])}% ({x['page']}): {x['alt']} -- "
                     + ("break the equation" if x["kind"] == "equation" else "re-lay the table")
                     + " in the source")
    return not data["over"], True, lines


PA11Y_MISSING_WARNING = """\
  pa11y: WARNING -- pa11y is not installed, so the accessibility audit was SKIPPED:
         the page was built and checked otherwise, but it has NOT been audited.
         To install: get Node.js (https://nodejs.org), then run `npm install -g pa11y`
         (./setup.sh offers this), or ask whoever administers this machine; then
         `./course.py check NN` (Windows: `python course.py check NN`) re-runs
         the checks without rebuilding."""


def check_lecture(nn, strict=False, no_pa11y=False):
    """Returns (ok, skipped): ok is the verdict; skipped names the browser
    checks that could not run -- the accessibility audit when pa11y is
    missing, the width check when Node or puppeteer is -- warnings, not
    failures, unless --strict."""
    page_dir = SITE / f"lecture{nn}"
    ok = True
    skipped = []
    if not (page_dir / "index.html").exists():
        print(f"  MISSING: {page_dir}/index.html (build it first)")
        return False, []

    # latexml log: errors, with the known libgs/depth class told apart
    log = WEB_AUX / "latexmlaux" / f"lecture{nn}.latexml.log"
    if log.exists():
        text = log.read_text(encoding="utf-8", errors="replace")
        errors = re.findall(r"^Error:(\S+)", text, re.M)
        dpth = [e for e in errors if e.startswith("expected:dpth")]
        other = [e for e in errors if not e.startswith("expected:dpth")]
        if other:
            print(f"  latexml: {len(other)} error(s) -- {sorted(set(other))}")
            ok = False
        if dpth:
            if libgs_available():
                print(f"  latexml: {len(dpth)} image-depth error(s) WITH libgs present -- investigate")
                ok = False
            else:
                print(f"  latexml: {len(dpth)} image-depth error(s) (dvisvgm has no Ghostscript library; "
                      "baseline-only, harmless for display figures -- install ghostscript to clear)")
    else:
        print("  latexml log missing")
        ok = False

    # page-level tripwires
    n_math = n_unparsed = n_imgs = 0
    for page in sorted(page_dir.glob("*.html")):
        html_text = page.read_text(encoding="utf-8", errors="replace")
        missing = html_text.count("[ALT MISSING")
        if missing:
            print(f"  {page.name}: {missing} [ALT MISSING] figure description(s)")
            ok = False
        for m in re.finditer(r"<img\b[^>]*>", html_text):
            tag = m.group(0)
            if "ltx_graphics" in tag:
                n_imgs += 1
                if re.search(r'alt=""', tag):
                    print(f"  {page.name}: figure <img> with EMPTY alt")
                    ok = False
        bare = bare_math_text(html_text)
        if bare:
            print(f"  {page.name}: bare-math-text {len(bare)} -- {bare[:3]}")
            ok = False
        leaks = overlay_leaks(html_text)
        if leaks:
            print(f"  {page.name}: overlay-leak {len(leaks)} -- an overlay spec printed as text: {sorted(set(leaks))[:3]}")
            ok = False
        n_math += html_text.count("<math")
        n_unparsed += html_text.count("ltx_math_unparsed")

    print(f"  checks: <math> {n_math} | unparsed {n_unparsed} | figures {n_imgs} | bare-math-text 0 | overlay-leak 0"
          if ok else f"  checks: <math> {n_math} | unparsed {n_unparsed} | figures {n_imgs}")

    # widths at the normal column (desktop-first calibration), before the audit
    if not no_pa11y:
        good, measured, lines = equation_widths(sorted(page_dir.glob("*.html")), strict)
        for line in lines:
            print("  " + line)
        ok = ok and good
        if not measured:
            skipped.append("widths NOT MEASURED")

    # pa11y, every page -- a missing pa11y warns and is reported on the PASS
    # line; it fails the check only under --strict
    if not no_pa11y and not which("pa11y"):
        if strict:
            print("  pa11y: NOT INSTALLED -- required by --strict")
            ok = False
        else:
            print(PA11Y_MISSING_WARNING)
            skipped.append("accessibility audit SKIPPED: pa11y not installed")
    else:
        pa_ok = True
        for page in sorted(page_dir.glob("*.html")):
            good, msg = pa11y_page(page, strict, no_pa11y)
            if not good:
                print(f"  pa11y {page.name}: {msg}")
                pa_ok = False
        ok = ok and pa_ok
        if not no_pa11y:
            print("  pa11y: clean" if pa_ok else "  pa11y: see above")
    return ok, skipped


# ---------------------------------------------------------------------------
# index
# ---------------------------------------------------------------------------

def build_index(strict=False, no_pa11y=False):
    meta = course_meta()
    rows = [(nn, lecture_title(nn)) for nn in lectures()]
    items = "\n".join(
        f"      <li><a href='lecture{nn}/index.html'>Lecture {int(nn)} — {title}</a></li>"
        for nn, title in rows)
    page = f"""<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{meta.get('coursecode', '')} — {meta.get('coursetitle', '')}</title>
<style>
  body {{ font-family: Georgia, serif; max-width: 42rem; margin: 2rem auto; padding: 0 1rem; color: #111827; }}
  h1 {{ color: #13294B; font-size: 1.5rem; }}
  nav ol {{ list-style: none; padding-left: 0; }}
  nav li {{ margin: 0.4rem 0; }}
  a {{ color: #13294B; }}
</style>
</head>
<body>
  <header>
    <h1>{meta.get('coursecode', '')} — {meta.get('coursetitle', '')}</h1>
    <p>Accessible HTML lecture notes, one page per lecture. {meta.get('courseterm', '')}.</p>
  </header>
  <nav aria-label="Lectures">
    <ol role="list">
{items}
    </ol>
  </nav>
</body>
</html>
"""
    SITE.mkdir(parents=True, exist_ok=True)
    out = SITE / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"index: {len(rows)} lecture(s) -> {out.relative_to(ROOT).as_posix()}")
    good, msg = pa11y_page(out, strict, no_pa11y)
    print(f"  pa11y: {msg}" if isinstance(msg, str) else "")
    return good


# ---------------------------------------------------------------------------
# doctor
# ---------------------------------------------------------------------------

def doctor():
    ok = True
    env = base_env()

    def probe(name, cmd, required=True, note=""):
        nonlocal ok
        exe = which(cmd[0], env)
        if not exe:
            print(f"  {'MISSING' if required else 'absent '}: {name}" + (f" ({note})" if note else ""))
            if required:
                ok = False
            return None
        rc, out = run(cmd, env=env, timeout=60)
        # the version line: the first naming the tool (latexmk on Windows
        # prints code-page chatter first), else simply the first
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        ver = next((l for l in lines if name.lower() in l.lower()), lines[0] if lines else "")
        print(f"  ok: {name} -- {ver[:70]}" + (f" ({note})" if note else ""))
        return out

    print("software the kit needs (expected on your PATH; KIT_TEXBIN adds a TeX directory first"
          + ("; KIT_STRAWBERRY names Strawberry Perl's folder if not C:\\Strawberry"
             if sys.platform == "win32" else "") + "):")
    print(f"  ok: python -- {sys.version.split()[0]}")
    make = make_exe(env)
    if make:
        probe("make", [make, "--version"],
              note="" if Path(make).stem == "make" else f"found as {Path(make).name.lower()}")
    else:
        print("  MISSING: make (GNU make -- on Windows, Strawberry Perl provides gmake)")
        ok = False
    probe("latexmk", ["latexmk", "--version"])
    probe("pdflatex", ["pdflatex", "--version"])
    probe("latexml", ["latexml", "--VERSION"], note="kit validated on 0.8.8 + classic-TeX preamble")
    dv = probe("dvisvgm", ["dvisvgm", "-V1"])
    if dv is not None and "Ghostscript" not in dv:
        print("  warn: dvisvgm has NO Ghostscript library (libgs) -- BookML image-depth "
              "errors expected (baseline-only); install ghostscript to clear")
    wired = base_env().get("LIBGS")
    if wired and not os.environ.get("LIBGS"):
        print(f"  note: LIBGS auto-wired to {wired} for dvisvgm")
    for sty in ("preview.sty", "comment.sty"):
        rc, out = run(["kpsewhich", sty], env=env, timeout=60)
        if rc == 0 and out.strip():
            print(f"  ok: {sty} -- {out.strip().splitlines()[0]}")
        else:
            print(f"  MISSING: {sty} (BookML needs it; install the TeX package)")
            ok = False
    if BOOKML.is_dir():
        print(f"  ok: bookml/ present")
    else:
        print("  MISSING: bookml/ -- run ./setup.sh to fetch the fixed release, or on "
              "Windows unzip it into bookml/ (docs/setup.md)")
        ok = False
    if puppeteer_dir(env):
        print(f"  ok: width check -- node + pa11y's puppeteer (equations and tables at most "
              f"{EQN_WIDTH_MAX:.0%} of the card at the {EQN_VIEWPORT} normal column)")
    else:
        print("  absent : width check -- needs Node.js and pa11y (its puppeteer); equations "
              "and tables are then NOT measured against the column")
    if which("pa11y", env):
        browser = pa11y_env().get("PUPPETEER_EXECUTABLE_PATH")
        fallback = system_browser()
        print(f"  ok: pa11y -- browser: {browser}" if browser else
              "  ok: pa11y -- browser: puppeteer's own"
              + (f", retried with {fallback} if it fails to launch" if fallback else ""))
    else:
        print("  absent : pa11y -- the accessibility audit will be skipped with a warning; "
              "install Node.js, then `npm install -g pa11y` (./setup.sh offers this)")

    meta = course_meta()
    print(f"course: {meta.get('coursecode', '?')} — {meta.get('coursetitle', '?')} "
          f"({meta.get('courseterm', '?')})")
    print("slides: " + ("lectured from (\\coursedecks yes) -- slides NN enforces slide fit"
                        if course_decks() else
                        "check only (\\coursedecks no) -- overfull frames reported, not enforced"))
    lex = lectures()
    print(f"content: {len(lex)} lecture(s): {', '.join(lex)}")
    for nn in lex:
        print(f"  lecture{nn}: {lecture_title(nn)}")
    return ok


# ---------------------------------------------------------------------------
# clean
# ---------------------------------------------------------------------------

def rmtree(path):
    """shutil.rmtree that also deletes read-only files: latexmlpost copies
    its stylesheets into each page folder read-only, and Windows refuses a
    plain delete of such a file (POSIX only needs the folder writable)."""
    def force(func, p, _exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=force)
    else:
        shutil.rmtree(path, onerror=force)


def clean(deep=False):
    for p in [BUILD] + sorted(ROOT.glob("lecture[0-9][0-9].tex")) \
            + sorted(ROOT.glob("*.zip")):
        if isinstance(p, Path) and p.exists():
            rmtree(p) if p.is_dir() else p.unlink()
            print(f"  removed {p.relative_to(ROOT)}")
    if deep:
        for p in (ROOT / "bmlimages",):
            if p.exists():
                rmtree(p)
                print(f"  removed {p.relative_to(ROOT)} (figure cache)")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("verb", choices=["build", "slides", "check", "figure",
                                     "index", "doctor", "clean"])
    ap.add_argument("lecture", nargs="?", help="NN / lectureNN (or --all)")
    ap.add_argument("name", nargs="?",
                    help="figure verb only: the figure basename (no .tex)")
    ap.add_argument("--all", action="store_true", help="every lecture in content/")
    ap.add_argument("--keep-announcements", action="store_true",
                    help="build: include the announcements sidecar in the web page (one-off)")
    ap.add_argument("--strict", action="store_true",
                    help="a missing pa11y, or a width check that could not run, is an error")
    ap.add_argument("--no-pa11y", action="store_true",
                    help="skip the browser checks -- the accessibility audit and the width check -- deliberately (the build says so)")
    ap.add_argument("--deep", action="store_true", help="clean: also drop the figure cache")
    args = ap.parse_args()

    if args.verb == "doctor":
        sys.exit(0 if doctor() else 1)
    if args.verb == "clean":
        clean(args.deep)
        return
    if args.verb == "index":
        sys.exit(0 if build_index(args.strict, args.no_pa11y) else 1)
    if args.verb == "figure":
        if not (args.lecture and args.name):
            sys.exit("usage: course.py figure NN figure-name")
        sys.exit(0 if render_figure(norm_lecture(args.lecture), args.name) else 1)

    targets = lectures() if args.all else [norm_lecture(args.lecture or "")] \
        if (args.lecture or args.all) else sys.exit("give a lecture (NN) or --all")

    results = {}
    for nn in targets:
        print(f"== lecture{nn} ==")
        if args.verb == "slides":
            results[nn] = build_slides(nn)
        elif args.verb in ("build", "check"):
            good, skipped = True, []
            if args.verb == "build":
                good = build_web(nn, args.keep_announcements)
            if good:
                good, skipped = check_lecture(nn, args.strict, args.no_pa11y)
            results[nn] = good
            print(("PASS" if good else "FAIL") + f" lecture{nn}"
                  + (f" ({'; '.join(skipped)} -- see the warning above)" if skipped else ""))
    if args.verb == "build" and args.all:
        build_index(args.strict, args.no_pa11y)
    n_ok = sum(results.values())
    print(f"\n{n_ok}/{len(results)} PASS")
    sys.exit(0 if n_ok == len(results) else 1)


if __name__ == "__main__":
    main()
