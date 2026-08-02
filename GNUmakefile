# Kit web build — BookML drives LaTeXML over the root-level lectureNN.tex
# wrappers that course.py generates (SOURCES set explicitly: the wrappers
# don't contain a literal \documentclass, so BookML's auto-scan misses them).
# bookml/ itself is fetched at a pinned release by the setup script.
SOURCES := $(wildcard lecture*.tex)
PDFTOSVG_CONVERTER = dvisvgm
include bookml/bookml.mk
