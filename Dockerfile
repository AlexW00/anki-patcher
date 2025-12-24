# syntax=docker/dockerfile:1.6

# Lightweight Python base image
FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps: keep minimal; build-essential helps when wheels are not available
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only what we need to build/install the package
COPY pyproject.toml /app/pyproject.toml
COPY README.md /app/README.md
COPY anki_patcher /app/anki_patcher

# Install the package using PEP 517 build backend (poetry-core). No Poetry CLI needed.
RUN pip install --upgrade pip \
    && pip install .

# Pre-download unidic so Japanese ops work out of the box
RUN python -m unidic download

# Default AnkiConnect endpoint inside Docker should target the host
# Users can override at runtime; compose sets this explicitly too.
ENV ANKI_CONNECT_URL=http://host.docker.internal:8765

# Default working directory where configs and mounted files live
WORKDIR /work

# Expose no ports; the app is a CLI that calls out to AnkiConnect

# Use the console entrypoint installed by the package
ENTRYPOINT ["anki-patcher"]
