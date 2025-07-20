# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    bash \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the add-on specific requirements and install Python dependencies
COPY addons/sterling_os/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary files from the repository
COPY sterling_core.py ./
COPY cognitive_router.py ./
COPY src/ ./src/
COPY modules/ ./modules/
COPY scripts/scaffold_phases.py ./

# Copy the add-on files
COPY addons/sterling_os/ ./sterling_os/

# Set up Python path and generate phase modules
ENV PYTHONPATH="/app:/app/sterling_os"
RUN python scaffold_phases.py || echo "Phase scaffolding completed"

# Make entrypoint executable
RUN chmod +x ./sterling_os/entrypoint.sh

# Create data directory for persistent storage
RUN mkdir -p /data

# Expose the service port
EXPOSE 5000

# Set environment variables for Home Assistant
ENV HOME_ASSISTANT_URL="http://supervisor/core"
ENV PYTHONPATH="/app:/app/sterling_os"

# Use the add-on's entrypoint
ENTRYPOINT ["./sterling_os/entrypoint.sh"]
