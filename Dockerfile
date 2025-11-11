FROM python:3.12-slim

# Install base system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    pdftk \
    wget \
    perl \
    ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install vanilla TeX Live with minimal scheme
# This layer is cached and only rebuilds if texlive.profile changes
COPY texlive.profile /tmp/texlive.profile
RUN wget -qO- https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz | tar -xz && \
    cd install-tl-* && \
    ./install-tl --profile=/tmp/texlive.profile && \
    cd .. && rm -rf install-tl-* /tmp/texlive.profile

# Add TeX Live to PATH (using fixed path from texlive.profile)
ENV PATH="/usr/local/texlive/bin/x86_64-linux:${PATH}"

# Install additional LaTeX packages and fonts
# This layer can be modified without re-downloading/installing base TeX Live
COPY .devcontainer/install-texlive-packages.sh /tmp/install-texlive-packages.sh
RUN tlmgr option -- autobackup 0 && \
    PACKAGES=$(bash /tmp/install-texlive-packages.sh) && \
    tlmgr install $PACKAGES && \
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
