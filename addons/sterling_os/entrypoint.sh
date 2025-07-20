#!/bin/bash

# Home Assistant Add-on: Sterling OS
# Alternative entrypoint script for the Sterling OS add-on
# Note: Home Assistant add-ons typically use run.sh as the primary entrypoint
# This script provides an alternative way to start the application

echo "Starting Sterling OS Add-on (via entrypoint.sh)..."

# Set up environment
export PYTHONPATH="/app:/app/sterling_os:$PYTHONPATH"
export HOME_ASSISTANT_URL="${HOME_ASSISTANT_URL:-http://supervisor/core}"
export HA_TOKEN="${HA_TOKEN:-}"

# Create data directory if it doesn't exist
mkdir -p /data

# Change to the sterling_os directory
cd /app/sterling_os

# Start the Sterling OS application
python3 main.py
