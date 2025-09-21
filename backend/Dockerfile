# Multi-stage build for optimized image size
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Build stage for dependencies
FROM base AS builder

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip cache purge

# Production stage
FROM base AS production

# Copy only installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/ /app/backend/
COPY ai-services/ /app/ai-services/

# Create necessary directories
RUN mkdir -p /app/logs /app/media /app/static

WORKDIR /app/backend/core

ENV PYTHONPATH=/app

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Web server variant
FROM production AS web
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "core.wsgi:application"]

# Celery worker variant
FROM production AS worker
CMD ["celery", "-A", "core", "worker", "-l", "info", "--concurrency=4"]

# Celery scheduler variant
FROM production AS scheduler
CMD ["celery", "-A", "core", "beat", "-l", "info", "--scheduler", "django_celery_beat.schedulers:DatabaseScheduler"]
