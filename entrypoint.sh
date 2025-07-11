#!/bin/bash
set -e

echo ">>> Pulling latest from Git..."
git pull origin main

echo ">>> Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

echo ">>> Starting Gunicorn server..."
exec gunicorn app:app -b 0.0.0.0:5000 --timeout 300
