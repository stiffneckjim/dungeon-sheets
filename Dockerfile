# Optimized Dockerfile for dungeon-sheets
# Uses vanilla TeX Live + tlmgr to install only required fonts (~10MB vs 600MB texlive-fonts-extra)
FROM python:3.12-slim

# Install base system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        pdftk \
        wget \
        perl \
        ca-certificates \
        gnupg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install vanilla TeX Live with minimal scheme
# This gives us tlmgr to install only the fonts we need
RUN wget -qO- https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz | tar -xz && \
    cd install-tl-* && \
    echo "selected_scheme scheme-basic" > texlive.profile && \
    echo "instopt_adjustpath 0" >> texlive.profile && \
    echo "tlpdbopt_install_docfiles 0" >> texlive.profile && \
    echo "tlpdbopt_install_srcfiles 0" >> texlive.profile && \
    ./install-tl --profile=texlive.profile && \
    cd .. && rm -rf install-tl-*

# Add TeX Live to PATH
ENV PATH="/usr/local/texlive/2024/bin/x86_64-linux:${PATH}"

# Install additional LaTeX packages needed for character sheets
RUN tlmgr install \
    # Core LaTeX packages
    latex-bin \
    latexmk \
    # Graphics and formatting
    graphics \
    graphicx \
    xcolor \
    geometry \
    fancyhdr \
    titlesec \
    enumitem \
    # Tables and lists
    array \
    booktabs \
    longtable \
    multirow \
    # Fonts - only the specific ones needed for fancy decorations
    lettrine \
    royal \
    gillius2 \
    kpfonts \
    bookman \
    contour \
    avantgar \
    fontenc \
    # Font tools
    fontaxes \
    mweights \
    # Utilities
    tools \
    amsmath \
    babel \
    hyperref

# Install texlive-fonts-recommended equivalent fonts
RUN tlmgr install \
    charter \
    cm-super \
    courier \
    helvetic \
    mathpazo \
    ncntrsbk \
    palatino \
    pxfonts \
    symbol \
    times \
    utopia \
    zapfchan \
    zapfding

WORKDIR /app

# Install Python dependencies
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and install
COPY . /app
RUN pip install --no-cache-dir -e /app

WORKDIR /build

ENTRYPOINT [ "python", "-m", "dungeonsheets.make_sheets" ]
CMD [ "--fancy", "--editable", "--recursive" ]
