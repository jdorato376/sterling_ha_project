#!/bin/bash
set -e

echo "Building Sterling OS add-on locally..."

# Check if we're in the right directory
if [ ! -f "addons/sterling_os/config.json" ]; then
    echo "Error: Please run this script from the repository root directory"
    exit 1
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t local/sterling_os:latest -f addons/sterling_os/Dockerfile .

echo "✅ Build complete!"
echo ""
echo "To use the local image:"
echo "1. Edit addons/sterling_os/config.json"
echo "2. Change the 'image' field to: 'local/sterling_os:latest'"
echo "3. Install the add-on in Home Assistant"