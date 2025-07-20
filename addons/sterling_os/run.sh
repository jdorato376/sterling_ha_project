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

# Ensure the sterling_os directory exists
if [ ! -d "/app/sterling_os" ]; then
    echo "Error: Directory /app/sterling_os does not exist. Creating it..."
    mkdir -p /app/sterling_os || { echo "Failed to create /app/sterling_os. Exiting."; exit 2; }
fi

# Change to the sterling_os directory
cd /app/sterling_os || { echo "Failed to change to directory /app/sterling_os. Exiting."; exit 3; }

# Verify that main.py exists
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found in /app/sterling_os. Exiting."
    exit 4
fi
# Start the Sterling OS application
echo "Launching Sterling OS main application..."
python3 main.py
