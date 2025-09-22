FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

FROM base AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        postgresql-client \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --user -r requirements.txt \
    && find /root/.local -name "*.pyc" -delete \
    && find /root/.local -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /root/.local -name "*.pyo" -delete \
    && find /root/.local -name "*.a" -delete \
    && find /root/.local -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /root/.local -name "test" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /root/.local -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true

FROM base AS production

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove -y

COPY --from=builder /root/.local /root/.local

COPY backend/core/ /app/backend/core/
COPY backend/apps/ /app/backend/apps/

WORKDIR /app/backend/core

ENV PYTHONPATH=/app
ENV PATH=/root/.local/bin:$PATH

RUN python manage.py collectstatic --noinput \
    && find /app -name "*.pyc" -delete \
    && find /app -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true \
    && rm -rf /tmp/* /var/tmp/*

EXPOSE 8000

FROM production AS web
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "core.wsgi:application"]

FROM production AS worker
CMD ["celery", "-A", "core", "worker", "-l", "info", "--concurrency=4"]

FROM production AS scheduler
CMD ["celery", "-A", "core", "beat", "-l", "info", "--scheduler", "django_celery_beat.schedulers:DatabaseScheduler"]
