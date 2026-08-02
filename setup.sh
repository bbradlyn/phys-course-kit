#!/usr/bin/env bash
# ===========================================================================
# Day-0 toolchain setup for phys-course-kit (macOS / Linux).
#
# Idempotent: checks first, asks before installing anything, and finishes by
# running `./course.py doctor` so you see the audited end state.
#   --yes      answer yes to every install prompt
#   --dry-run  report what would be done, change nothing
# Windows: this is a POSIX script — follow the manual steps in docs/setup.md.
# ===========================================================================
set -u
cd "$(dirname "$0")"

BOOKML_VERSION="v0.29.4"
BOOKML_SHA256="1ec8c79f47c3f2e434a05e9d30b38235e67ab973fdff22853f2577a3de6811e5"
BOOKML_URL="https://github.com/vlmantova/bookml/releases/download/${BOOKML_VERSION}/release.zip"

DRY=0; YES=0
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    --yes)     YES=1 ;;
    *) echo "usage: $0 [--yes] [--dry-run]"; exit 2 ;;
  esac
done

say()  { printf '%s\n' "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }
confirm() {
  [ "$YES" = 1 ] && return 0
  [ "$DRY" = 1 ] && return 1
  printf '%s [y/N] ' "$1"; read -r r; case "$r" in y|Y|yes|YES) return 0;; *) return 1;; esac
}
act() {  # act "description" cmd args...
  local desc="$1"; shift
  if [ "$DRY" = 1 ]; then say "  would: $desc  ->  $*"; return 0; fi
  say "  doing: $desc"; "$@"
}

FAIL=0

say "== TeX Live =="
for t in pdflatex latexmk dvisvgm kpsewhich; do
  if have "$t"; then say "  ok: $t"; else
    say "  MISSING: $t — install a full TeX Live first"
    say "    macOS: https://tug.org/mactex/    Linux: your distro's texlive-full"
    FAIL=1
  fi
done

if have kpsewhich; then
  say "== TeX packages BookML needs =="
  missing=""
  for sty in preview.sty comment.sty; do
    if kpsewhich "$sty" >/dev/null 2>&1; then say "  ok: $sty"; else
      say "  missing: $sty"; missing="$missing ${sty%.sty}"
    fi
  done
  if [ -n "$missing" ] && have tlmgr; then
    if confirm "install$missing via tlmgr? (may need sudo on a system TeX Live)"; then
      act "tlmgr install$missing" tlmgr install $missing \
        || say "  tlmgr failed — try: sudo tlmgr install$missing"
    else
      [ "$DRY" = 1 ] && say "  would ask to: tlmgr install$missing"
    fi
  fi
fi

say "== LaTeXML =="
if have latexml; then
  say "  ok: $(latexml --VERSION 2>&1)"
else
  if have brew; then
    if confirm "install LaTeXML via Homebrew?"; then
      act "brew install latexml" brew install latexml || FAIL=1
    else
      [ "$DRY" = 1 ] && say "  would ask to: brew install latexml"; FAIL=1
    fi
  else
    say "  MISSING: latexml — install via your package manager or 'cpanm LaTeXML'"; FAIL=1
  fi
fi

say "== Ghostscript library (dvisvgm needs libgs for BookML image baselines) =="
if have dvisvgm && dvisvgm -V1 2>/dev/null | grep -q Ghostscript; then
  say "  ok: dvisvgm has Ghostscript support"
elif [ -e /opt/homebrew/lib/libgs.dylib ] || [ -e /usr/local/lib/libgs.dylib ]; then
  say "  ok: libgs present — course.py points dvisvgm at it automatically (LIBGS)"
else
  if have brew; then
    if confirm "install ghostscript via Homebrew (provides libgs)?"; then
      act "brew install ghostscript" brew install ghostscript \
        || say "  install failed — image-depth errors will persist (baseline-only, non-fatal)"
    else
      [ "$DRY" = 1 ] && say "  would ask to: brew install ghostscript"
      say "  skipped — expect harmless image-depth warnings until installed"
    fi
  else
    say "  install ghostscript (with its shared library) via your package manager"
    say "  until then: harmless image-depth warnings on figure-bearing builds"
  fi
fi

say "== BookML (pinned ${BOOKML_VERSION}) =="
if grep -qs "\$bmlVersion = '${BOOKML_VERSION}'" bookml/bookml.sty.ltxml; then
  say "  ok: bookml/ already at ${BOOKML_VERSION}"
else
  if [ -d bookml ]; then say "  bookml/ present but not ${BOOKML_VERSION} — refreshing"; fi
  if [ "$DRY" = 1 ]; then
    say "  would: download ${BOOKML_URL}, verify sha256, unpack to bookml/"
  else
    tmp="$(mktemp -d)"
    say "  fetching ${BOOKML_URL}"
    if curl -fsSL -o "$tmp/release.zip" "$BOOKML_URL"; then
      got="$(shasum -a 256 "$tmp/release.zip" | cut -d' ' -f1)"
      if [ "$got" = "$BOOKML_SHA256" ]; then
        rm -rf bookml
        unzip -q "$tmp/release.zip" -d "$tmp/unpacked" && mv "$tmp/unpacked/bookml" bookml
        say "  ok: bookml/ installed at ${BOOKML_VERSION} (checksum verified)"
      else
        say "  CHECKSUM MISMATCH — refusing to install (expected ${BOOKML_SHA256}, got ${got})"
        FAIL=1
      fi
    else
      say "  download failed"; FAIL=1
    fi
    rm -rf "$tmp"
  fi
fi

say "== pa11y (optional accessibility audits) =="
if have pa11y; then say "  ok: pa11y"; else
  if have npm; then
    if confirm "install pa11y via npm -g?"; then
      act "npm install -g pa11y" npm install -g pa11y || say "  npm install failed — audits will be skipped"
    else
      [ "$DRY" = 1 ] && say "  would ask to: npm install -g pa11y"
      say "  skipped — course.py will skip audits until installed"
    fi
  else
    say "  no npm — install Node.js, then: npm install -g pa11y (audits skipped meanwhile)"
  fi
fi

say ""
if [ "$DRY" = 1 ]; then
  say "(dry run — nothing changed; the doctor report below reflects the CURRENT state)"
fi
say "== course.py doctor =="
./course.py doctor
rc=$?
[ "$FAIL" = 1 ] && exit 1
exit $rc
