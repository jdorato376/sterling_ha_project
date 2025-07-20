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

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the add-on files
COPY . /app/sterling_os/
COPY ../../sterling_core.py /app/
COPY ../../cognitive_router.py /app/
COPY ../../src/ /app/src/
COPY ../../modules/ /app/modules/
COPY ../../scripts/scaffold_phases.py /app/

# Set up Python path and generate phase modules
ENV PYTHONPATH="/app:/app/sterling_os"
RUN python scaffold_phases.py

# Make entrypoint executable
RUN chmod +x /app/sterling_os/entrypoint.sh

# Create data directory for persistent storage
RUN mkdir -p /data

# Expose the service port
EXPOSE 5000

# Use the add-on's entrypoint
ENTRYPOINT ["/app/sterling_os/entrypoint.sh"]
