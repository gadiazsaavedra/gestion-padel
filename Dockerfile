# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# --- Builder stage ---
FROM base AS builder

# Copy only requirements.txt first for better cache usage
COPY --link requirements.txt ./

# Create virtual environment and install dependencies using pip cache
RUN python -m venv .venv \
    && .venv/bin/pip install --upgrade pip \
    && --mount=type=cache,target=/root/.cache/pip \
       .venv/bin/pip install -r requirements.txt

# --- Final stage ---
FROM base AS final

# Create a non-root user
RUN useradd -m appuser
USER appuser

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code (excluding .git, .env, IDE, venv, node_modules, etc.)
COPY --link . .

# Create media, staticfiles and logs directories if not present
RUN mkdir -p /app/media /app/staticfiles /app/logs

# Expose Django's default port
EXPOSE 8000

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
