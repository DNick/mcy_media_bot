# syntax=docker/dockerfile:1

# --- Стадия сборки: ставим зависимости в .venv через uv ---
FROM python:3.14-slim AS builder

# Бинарник uv из официального образа.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Зависимости — отдельный кешируемый слой (без самого проекта).
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Исходники + установка самого проекта.
COPY README.md main.py config.py media.py logo.png ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# --- Финальная стадия: только рантайм, без uv и кешей сборки ---
FROM python:3.14-slim

# ffmpeg-python требует системный бинарник ffmpeg для обработки видео.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Непривилегированный пользователь + готовое окружение и код из builder.
RUN useradd --create-home --uid 1000 appuser
COPY --from=builder --chown=appuser:appuser /app /app

USER appuser

CMD ["python", "main.py"]
