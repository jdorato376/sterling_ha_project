#!/usr/bin/env bash

# Home Assistant Add-on: Sterling OS
# Main entrypoint script for the Sterling OS add-on
# This script is the primary entry point that Home Assistant will execute

set -e

echo "Starting Sterling OS Home Assistant Add-on..."

# Set up environment variables
export PYTHONPATH="/app:/app/sterling_os:${PYTHONPATH}"
export HOME_ASSISTANT_URL="${HOME_ASSISTANT_URL:-http://supervisor/core}"
export HA_TOKEN="${HA_TOKEN:-}"

# Create data directory if it doesn't exist
mkdir -p /data

# Change to the sterling_os directory
cd /app/sterling_os

# Start the Sterling OS application
echo "Launching Sterling OS main application..."
python3 main.py
