FROM python:3.12-slim

# Install system dependencies in a single layer and clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        pdftk \
        texlive-latex-base \
        texlive-latex-extra \
        texlive-fonts-recommended && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

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
