# Home Assistant Add-on: Sterling OS
# Sterling: Executive AI Assistant Add-on with Gemini & Ollama Routing
# This Dockerfile builds the Sterling OS add-on for Home Assistant

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
# Note: In Home Assistant add-on context, we're already in the add-on directory
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary files from the repository root
# These files need to be copied from the repository context
COPY ../../sterling_core.py ./
COPY ../../cognitive_router.py ./
COPY ../../src/ ./src/
COPY ../../modules/ ./modules/

# Copy the scaffold script if it exists
RUN [ -f "../../scripts/scaffold_phases.py" ] && cp ../../scripts/scaffold_phases.py ./ || echo "No scaffold script found"

# Copy all add-on files to the working directory
COPY . ./sterling_os/

# Set up Python path and generate phase modules if scaffold script exists
ENV PYTHONPATH="/app:/app/sterling_os"
RUN python scaffold_phases.py 2>/dev/null || echo "Phase scaffolding skipped"

# Make run script executable (Home Assistant add-ons expect run.sh)
RUN chmod +x ./sterling_os/run.sh

# Create data directory for persistent storage
RUN mkdir -p /data

# Expose the service port
EXPOSE 5000

# Set environment variables for Home Assistant
ENV HOME_ASSISTANT_URL="http://supervisor/core"
ENV PYTHONPATH="/app:/app/sterling_os"

# Home Assistant add-ons use run.sh as the default entrypoint
CMD ["./sterling_os/run.sh"]
