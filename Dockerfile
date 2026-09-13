# Stage 1: Build virtualenv using astral-sh/uv
FROM ghcr.io/astral-sh/uv:0.9.8 AS uv

FROM python:3.12-slim AS builder
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Copy uv binary from official uv image
COPY --from=uv /uv /uvx /bin/

# Copy dependency declarations
COPY pyproject.toml uv.lock ./

# Install dependencies into /app/.venv using cache mount
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Stage 2: Minimal runtime image
FROM python:3.12-slim AS runner

WORKDIR /app

# Create non-root user and persistent data directory
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/bash -m appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appgroup /app

# Copy pre-built virtual environment
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --from=uv /uv /bin/uv

# Set environment paths and variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL="sqlite:///./data/kanban.db"

# Copy application source code
COPY --chown=appuser:appgroup app/ /app/app/
COPY --chown=appuser:appgroup pyproject.toml /app/

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
