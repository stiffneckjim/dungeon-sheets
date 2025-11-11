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
)

# Join array with spaces
echo "${TEXLIVE_PACKAGES[*]}"
