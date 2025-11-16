FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# Install system dependencies needed for TeX Live
RUN apt-get update && apt-get install -y --no-install-recommends \
    pdftk-java \
    wget \
    perl \
    libwww-perl \
    fontconfig \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# Install vanilla TeX Live with minimal scheme
COPY texlive.profile /tmp/texlive.profile
RUN echo "Downloading TeX Live installer..." && \
    wget -qO- https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz | tar -xz -C /tmp && \
    cd /tmp/install-tl-* && \
    echo "Installing TeX Live (this may take a few minutes)..." && \
    ./install-tl --profile=/tmp/texlive.profile -v && \
    echo "TeX Live installation complete!" && \
    cd / && rm -rf /tmp/install-tl-* /tmp/texlive.profile

# Add TeX Live to PATH for both architectures
ENV PATH="/usr/local/texlive/bin/x86_64-linux:/usr/local/texlive/bin/aarch64-linux:${PATH}"

# Install additional LaTeX packages
COPY .devcontainer/install-texlive-packages.sh /tmp/install-texlive-packages.sh
RUN echo "Configuring tlmgr..." && \
    tlmgr option -- autobackup 0 && \
    PACKAGES=$(bash /tmp/install-texlive-packages.sh) && \
    echo "Installing LaTeX packages: $PACKAGES" && \
    tlmgr install $PACKAGES && \
    echo "LaTeX package installation complete!" && \
    rm /tmp/install-texlive-packages.sh

# Install Kalam fonts for MSavage template
RUN mkdir -p /usr/share/fonts/truetype/kalam && \
    cd /tmp && \
    wget -q https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Regular.ttf && \
    wget -q https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Bold.ttf && \
    wget -q https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Light.ttf && \
    mv Kalam-*.ttf /usr/share/fonts/truetype/kalam/ && \
    fc-cache -fv && \
    rm -rf /tmp/*

WORKDIR /workspaces
