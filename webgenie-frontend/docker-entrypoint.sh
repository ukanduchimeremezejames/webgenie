#!/bin/sh

# Docker entrypoint for frontend
# This script handles environment variable substitution before starting nginx

# Function to log messages
log() {
    echo "[ENTRYPOINT] $1"
}

log "Starting WebGenie Frontend..."

# Get the API URL from environment or use default
API_URL="${VITE_API_URL:-http://localhost:8000/api/v1}"
log "API URL: $API_URL"

# Update nginx configuration with the correct API URL
if [ -z "$API_URL" ]; then
    log "ERROR: VITE_API_URL is not set"
    exit 1
fi

# Execute the command
exec "$@"
