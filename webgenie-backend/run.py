"""
FastAPI and Uvicorn startup configuration for production.
"""

import os
from pathlib import Path

# Environment
debug = os.getenv("DEBUG", "False").lower() == "true"
log_level = os.getenv("LOG_LEVEL", "INFO").lower()

# Server configuration
host = os.getenv("SERVER_HOST", "0.0.0.0")
port = int(os.getenv("SERVER_PORT", "8000"))
workers = int(os.getenv("SERVER_WORKERS", "4"))

# Uvicorn configuration
uvicorn_config = {
    "app": "app.main:app",
    "host": host,
    "port": port,
    "log_level": log_level,
    "access_log": True,
    "use_colors": not debug,
    "reload": debug,
    "workers": workers if not debug else 1,
}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(**uvicorn_config)
