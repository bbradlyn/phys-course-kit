# BookML CONFIGURATION — not the kit's build system.
#
# The kit's one-command driver is course.py; you never run `make` yourself.
# BookML, however, is a make-based tool: its whole web pipeline ships as
# bookml/bookml.mk, and its documented interface is a makefile that sets a
# few variables and includes it. This file is that configuration, and
# `course.py build` invokes it the way `course.py slides` invokes latexmk —
# as a tool's entry point.
#
# Settings: BookML builds the root-level lectureNN.tex wrappers course.py
# generates (SOURCES is explicit because the wrappers don't contain a literal
# \documentclass, which BookML's auto-scan greps for); outputs land under
# build/web; bookml/ itself is fetched at a pinned release by the setup
# script.
SOURCES := $(wildcard lecture*.tex)
AUX_DIR := build/web
PDFTOSVG_CONVERTER = dvisvgm
# Kit styling: a light CSS layer over BookML's plain style (loads last, wins ties)
LATEXMLPOSTEXTRAFLAGS += --css=shared/kit.css
include bookml/bookml.mk
