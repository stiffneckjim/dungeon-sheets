#!/bin/bash
# Shared TeX Live package installation list
# Used by both Dockerfile and devcontainer setup.sh

TEXLIVE_PACKAGES=(
    collection-latexrecommended
    # XeLaTeX support for MSavage template
    xetex
    fontspec
    kpfonts-otf         # OpenType Kp-fonts for XeLaTeX
    pstricks            # PostScript tricks for drawing
    # Standard packages
    xcolor
    fontaxes
    booktabs
    enumitem
    lettrine
    kpfonts
    bookman
    courier
    gillius
    contour
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
    luacolor
    minifp
    multitoc
    xstring
)

# Join array with spaces
echo "${TEXLIVE_PACKAGES[*]}"
