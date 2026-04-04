#!/bin/bash
# Shared TeX Live package installation list
# Used by both Dockerfile and devcontainer setup.sh

TEXLIVE_PACKAGES=(
    collection-latexrecommended
    xcolor
    fontaxes
    booktabs
    enumitem
    lettrine
    kpfonts
    kpfonts-otf
    bookman
    courier
    gillius
    contour
    pstricks
    pst-tools
    currfile
    avantgar
    needspace
    supertabular
    etoolbox
    hyperref
    geometry
    fancyhdr
    caption
    graphics-def
    epstopdf-pkg
    # Packages required for fancy D&D decorations
    cfr-initials        # Royal font
    gensymb
    was
    hang
    numprint
    tcolorbox
    environ
    trimspaces
    pdfcol
    tikzfill
    tocloft
    titlesec
    initials
    keycommand
    lipsum
    luatex
    luacolor
    luaotfload
    luapstricks
    fontspec
    minifp
    multitoc
    xstring
)

# Join array with spaces
echo "${TEXLIVE_PACKAGES[*]}"
