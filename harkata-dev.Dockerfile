FROM ghcr.io/astral-sh/uv:python3.13-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy files required for uv sync
COPY pyproject.toml README.md ./
