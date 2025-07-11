#!/bin/bash

echo "🚀 Sterling Phase 3 Automation Script Starting..."

# Step 1: Navigate to project root
cd ~/sterling_ha_project || { echo "❌ Directory not found"; exit 1; }

# Step 2: Pull latest from origin and switch to correct branch
git fetch --all
git checkout -B context-phase-3 origin/context-phase-3

# Step 3: Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Step 4: Upgrade pip
pip install --upgrade pip

# Step 5: Install primary dependencies
pip install -r requirements.txt

# Step 6: Install Sterling OS add-on dependencies (Ollama, Twilio, OpenAI, etc.)
pip install -r addons/sterling_os/requirements.txt

# Step 7: Run tests to confirm integrity
pytest -q || { echo "❌ Tests failed"; exit 1; }

# Step 8: Launch app
echo "✅ All systems go. Launching Sterling API server on http://localhost:5000"
python app.py
