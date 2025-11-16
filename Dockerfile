FROM python:3.12-slim AS dungeonsheets

# Install base system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    pdftk \
    gnupg \
    wget \
    xz-utils \
    perl \
    libwww-perl \
    fontconfig \
    ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install vanilla TeX Live with minimal scheme
# This layer is cached and only rebuilds if texlive.profile changes
COPY texlive.profile /tmp/texlive.profile
RUN echo "Downloading TeX Live installer..." && \
    cd /tmp/ && \
    wget https://tex.org.uk/systems/texlive/tlnet/install-tl-unx.tar.gz && \
    zcat < install-tl-unx.tar.gz | tar xf - && \
    cd install-tl-2* && \
    echo "Installing TeX Live (this may take a few minutes)..." && \
    perl ./install-tl -v \
    --profile=/tmp/texlive.profile \
    --repository https://tex.org.uk/systems/texlive/tlnet/ && \
    echo "TeX Live installation complete!" && \
    cd .. && rm -rf install-tl-* /tmp/texlive.profile

# Add TeX Live to PATH (detect architecture: x86_64-linux or aarch64-linux)
# Use the first directory found in /usr/local/texlive/bin/
RUN TEXLIVE_BIN=$(find /usr/local/texlive/bin -maxdepth 1 -type d -name '*-linux' | head -1) && \
    echo "export PATH=\"${TEXLIVE_BIN}:\$PATH\"" >> /etc/profile.d/texlive.sh && \
    echo "Found TeX Live binaries at: ${TEXLIVE_BIN}"
ENV PATH="/usr/local/texlive/bin/x86_64-linux:/usr/local/texlive/bin/aarch64-linux:${PATH}"

# Install additional LaTeX packages and fonts
# This layer can be modified without re-downloading/installing base TeX Live
COPY .devcontainer/install-texlive-packages.sh /tmp/install-texlive-packages.sh
RUN echo "Configuring tlmgr..." && \
    tlmgr option -- autobackup 0 && \
    PACKAGES=$(bash /tmp/install-texlive-packages.sh) && \
    echo "Installing LaTeX packages: $PACKAGES" && \
    tlmgr install $PACKAGES && \
    echo "LaTeX package installation complete!" && \
    rm /tmp/install-texlive-packages.sh

# Install Kalam fonts for MSavage template
RUN echo "Installing Kalam fonts..." && \
    mkdir -p /usr/share/fonts/truetype/kalam && \
    wget -q https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Regular.ttf && \
    wget -q https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Bold.ttf && \
    wget -q https://github.com/google/fonts/raw/main/ofl/kalam/Kalam-Light.ttf && \
    mv Kalam-*.ttf /usr/share/fonts/truetype/kalam/ && \
    fc-cache -fv && \
    echo "Kalam fonts installation complete!"

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

FROM dungeonsheets AS devcontainer

# Install development tools and dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    less \
    pipx \
    unzip \
    starship \
    zsh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Add a non-root user for development
RUN echo "Creating vscode user" && \
    useradd -m -s /bin/bash vscode && \
    chown -R vscode:vscode /app /build && \
    chsh -s /bin/zsh vscode

USER vscode

# Install Python development tools with pipx
RUN echo "Installing pipx and tools" && \
    pipx install argcomplete && \
    pipx install black && \
    pipx install coverage && \
    pipx install flake8 && \
    pipx install mypy && \
    pipx install pyflakes && \
    pipx install pylint && \
    pipx install pytest

# Install Node development container with fnm
RUN echo "Installing fnm and Node.js" && \
    curl -fsSL https://fnm.vercel.app/install | bash -s -- --skip-shell && \
    ln -s /home/vscode/.local/share/fnm/fnm /home/vscode/.local/bin && \
    /home/vscode/.local/bin/fnm install --lts

WORKDIR /workspaces/dungeonsheets
