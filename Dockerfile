# -------------------------------------------------------
# Stage 1: Builder
# -------------------------------------------------------
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# Only install what is needed for pip builds — NO compilers
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --user --no-cache-dir -r requirements.txt

# -------------------------------------------------------
# Stage 2: Runtime
# -------------------------------------------------------
FROM python:3.11-slim-bookworm

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH="/root/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY ./app /app/app
COPY ./.env.example /app/.env

RUN mkdir -p /data/results /data/datasets /var/log/webgenie

# Choreo-compliant user (UID must be 10000–20000)
RUN useradd -m -u 10001 webgenie && \
    chown -R webgenie:webgenie /app /data /var/log/webgenie

USER 10001

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
