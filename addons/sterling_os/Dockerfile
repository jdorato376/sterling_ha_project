# Sterling HA Project - Multi-stage Dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Build stage for dependencies
FROM base AS builder

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Production stage
FROM base AS production

# Copy wheels from builder stage
COPY --from=builder /wheels /wheels

# Install dependencies from wheels
RUN pip install --no-cache-dir --find-links /wheels --no-index \
    $(cat requirements.txt | grep -v "^#" | grep -v "^$") \
    && rm -rf /wheels

# Copy application code
COPY src/ /app/src/
COPY modules/ /app/modules/
COPY scripts/scaffold_phases.py /app/scaffold_phases.py

# Copy add-on specific files
COPY addons/sterling_os/run.sh /app/run.sh
COPY addons/sterling_os/config.json /app/config.json

# Make run script executable
RUN chmod +x /app/run.sh

# Run scaffolding to generate phase modules
RUN python /app/scaffold_phases.py

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash sterling
RUN chown -R sterling:sterling /app
USER sterling

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Set entrypoint
ENTRYPOINT ["./run.sh"]
