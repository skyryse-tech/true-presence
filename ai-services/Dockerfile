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
        cmake \
        libopencv-dev \
        python3-opencv \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
        git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY ai-services/requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --user -r requirements.txt \
    && find /root/.local -name "*.pyc" -delete \
    && find /root/.local -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /root/.local -name "*.pyo" -delete \
    && find /root/.local -name "*.a" -delete \
    && find /root/.local -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /root/.local -name "test" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /root/.local -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /root/.local -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /root/.local -name "*.whl" -delete \
    && find /root/.local -name "*.tar.gz" -delete

FROM base AS production

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libopencv-dev \
        python3-opencv \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove -y

COPY --from=builder /root/.local /root/.local

COPY ai-services/ /app/ai-services/

ENV PYTHONPATH=/app
ENV PATH=/root/.local/bin:$PATH

RUN find /app -name "*.pyc" -delete \
    && find /app -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true \
    && rm -rf /tmp/* /var/tmp/*

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health/ || exit 1

CMD ["python", "ai-services/worker.py"]
