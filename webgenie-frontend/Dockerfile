# -------------------------------------------------------
# Stage 1: Builder
# -------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --user --no-cache-dir -r requirements.txt

# -------------------------------------------------------
# Stage 2: Runtime Image
# -------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# Copy built Python packages
COPY --from=builder /root/.local /root/.local
ENV PATH="/root/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy source
COPY ./app /app/app
COPY ./.env.example /app/.env

RUN mkdir -p /data/results /data/datasets /var/log/webgenie

# Choreo-compliant user (MUST be 10000–20000)
RUN useradd -m -u 10001 webgenie && \
    chown -R webgenie:webgenie /app /data /var/log/webgenie

USER 10001

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
