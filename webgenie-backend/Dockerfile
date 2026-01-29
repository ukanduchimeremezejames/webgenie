# -------------------------------------------------------
# Stage 1: Builder
# -------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system build dependencies (only in builder stage)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install dependencies in a clean layer
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --user --no-cache-dir -r requirements.txt

# -------------------------------------------------------
# Stage 2: Final Runtime Image
# -------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# NOTE: DO NOT install docker.io or build-essential here.
# Keep runtime image minimal to pass Dockerfile scans.

# Copy only the installed site-packages from builder
COPY --from=builder /root/.local /root/.local

ENV PATH="/root/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy source code
COPY ./app /app/app
COPY ./.env.example /app/.env

# Create directories
RUN mkdir -p /data/results /data/datasets /var/log/webgenie

# Create non-root user
RUN useradd -m -u 1000 webgenie && \
    chown -R webgenie:webgenie /app /data /var/log/webgenie
USER webgenie

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Entrypoint
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
