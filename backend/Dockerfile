FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN mkdir -p /app/logs /app/media /app/static

WORKDIR /app/backend/core

ENV PYTHONPATH=/app

RUN PYTHONPATH=/app python manage.py collectstatic --noinput

EXPOSE 8000

FROM base as web
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1
CMD ["sh", "-c", "PYTHONPATH=/app gunicorn --bind 0.0.0.0:8000 --workers 3 core.wsgi:application"]

FROM base as worker
CMD ["sh", "-c", "PYTHONPATH=/app celery -A core worker -l info --concurrency=4"]

FROM base as scheduler
CMD ["sh", "-c", "PYTHONPATH=/app celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"]
