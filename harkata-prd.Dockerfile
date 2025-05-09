FROM ghcr.io/astral-sh/uv:python3.13-bookworm

# EXPOSE 5000 # This is default value expected by Dokku

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src

RUN uv sync

CMD ["sh", "-c", "fastapi run src/main.py --host 0.0.0.0 --port ${PORT:-5000} --proxy-headers"]
