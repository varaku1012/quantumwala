# Analytics Dashboard ML Service - Multi-stage Dockerfile

# ===================
# Base Stage
# ===================
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# ===================
# Development Stage
# ===================
FROM base AS development

# Install all dependencies (including development packages)
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Install additional development tools
RUN pip install \
    black \
    isort \
    flake8 \
    mypy \
    pytest-watch \
    jupyter \
    ipython

# Copy source code
COPY . .

# Create non-root user
RUN groupadd -r mluser && useradd -r -g mluser mluser

# Create directories and set permissions
RUN mkdir -p /app/models /app/logs /app/data && \
    chown -R mluser:mluser /app

# Switch to non-root user
USER mluser

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Start the application in development mode
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload", "--log-level", "info"]

# ===================
# Build Stage
# ===================
FROM base AS build

# Install production dependencies only
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy source code
COPY . .

# Compile Python files for better performance
RUN python -m compileall .

# ===================
# Production Stage
# ===================
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.local/bin:$PATH"

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r mluser && useradd -r -g mluser mluser

# Set working directory
WORKDIR /app

# Copy built application from build stage
COPY --from=build --chown=mluser:mluser /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build --chown=mluser:mluser /usr/local/bin /usr/local/bin
COPY --from=build --chown=mluser:mluser /app .

# Create necessary directories
RUN mkdir -p /app/models /app/logs /app/data && \
    chown -R mluser:mluser /app

# Switch to non-root user
USER mluser

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4", "--log-level", "info"]

# ===================
# Training Stage
# ===================
FROM development AS training

# Install additional ML training tools
RUN pip install \
    mlflow \
    wandb \
    optuna \
    tensorboard

# Copy training scripts and data
COPY --chown=mluser:mluser training/ ./training/
COPY --chown=mluser:mluser data/ ./data/

# Start training job
CMD ["python", "training/train_models.py"]

# ===================
# Testing Stage
# ===================
FROM development AS testing

# Install testing dependencies
RUN pip install \
    pytest \
    pytest-asyncio \
    pytest-cov \
    httpx \
    faker

# Copy test files
COPY --chown=mluser:mluser tests/ ./tests/

# Run tests with coverage
CMD ["pytest", "tests/", "--cov=.", "--cov-report=html", "--cov-report=term"]

# ===================
# Jupyter Stage (for development/analysis)
# ===================
FROM development AS jupyter

# Install Jupyter and extensions
RUN pip install \
    jupyterlab \
    jupyter-dash \
    ipywidgets \
    plotly \
    seaborn

# Copy notebooks
COPY --chown=mluser:mluser notebooks/ ./notebooks/

# Expose Jupyter port
EXPOSE 8888

# Start Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''"]