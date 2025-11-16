FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    pdftk-java \
    wget \
    perl \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Install TeX Live
WORKDIR /tmp
RUN wget -q https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz \
    && tar -xzf install-tl-unx.tar.gz \
    && cd install-tl-* \
    && cat > texlive.profile << 'EOF'
selected_scheme scheme-basic
TEXDIR /usr/local/texlive
TEXMFLOCAL /usr/local/texlive/texmf-local
TEXMFSYSVAR /usr/local/texlive/texmf-var
TEXMFSYSCONFIG /usr/local/texlive/texmf-config
TEXMFVAR /root/.texlive/texmf-var
TEXMFCONFIG /root/.texlive/texmf-config
TEXMFHOME /root/texmf
option_doc 0
option_src 0
instopt_adjustpath 1
EOF

# Run TeX Live installer
RUN cd install-tl-* && perl ./install-tl --profile=texlive.profile --no-interaction

# Cleanup
RUN rm -rf /tmp/*

# Add TeX Live to PATH
ENV PATH="/usr/local/texlive/bin/x86_64-linux:${PATH}"

WORKDIR /workspaces
