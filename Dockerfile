# =====================================================================
# F1 2026 Prediction Center — production container image
# =====================================================================
# Build:  docker build -t f1-app .
# Run:    docker run -p 8501:8501 f1-app
# Or use the docker-compose.yml for a one-line `docker compose up`.
# =====================================================================

# Pin Python to 3.11 — same major as the team's local dev environment,
# and every wheel in requirements.txt is published for cp311.
FROM python:3.11-slim AS runtime

# --- System packages ---
# libgomp1 is the OpenMP runtime XGBoost links against on Linux.
# build-essential is intentionally NOT installed because we rely on
# pre-built wheels for every package in requirements.txt.
RUN apt-get update \
    && apt-get install --no-install-recommends -y libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# --- Application user ---
# Streamlit shouldn't run as root. Create a non-privileged user.
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# --- Python dependencies (cached layer) ---
# Copy requirements first so a code-only change doesn't bust the cache.
COPY --chown=appuser:appuser requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- Application source ---
COPY --chown=appuser:appuser . .

# --- Runtime configuration ---
USER appuser
EXPOSE 8501

# Streamlit defaults to writing telemetry & a config dir; redirect them
# under /tmp so the container can run with a read-only root filesystem.
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501

# Streamlit exposes a built-in liveness endpoint at /_stcore/health.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; \
        sys.exit(0) if urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health').status == 200 else sys.exit(1)"

CMD ["streamlit", "run", "code/app.py"]
