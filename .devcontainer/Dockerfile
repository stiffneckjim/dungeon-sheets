FROM mcr.microsoft.com/vscode/devcontainers/python

# Install base system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    pdftk \
    wget \
    gnupg \
    xz-utils \
    perl \
    ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install vanilla TeX Live with minimal scheme
# This layer is cached and only rebuilds if texlive.profile changes
COPY texlive.profile /tmp/texlive.profile
RUN echo "Downloading TeX Live installer..." && \
    wget -qO- https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz | tar -xz && \
    cd install-tl-* && \
    echo "Installing TeX Live (this may take a few minutes)..." && \
    ./install-tl --profile=/tmp/texlive.profile -v && \
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
