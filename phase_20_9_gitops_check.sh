#!/bin/bash

# Phase 20.9: GitOps Readiness Audit for Sterling Sovereignty Stack
# Runs a series of checks ensuring the repository is correctly configured.

set -e

cd /config || exit 1

echo "\U1F4D8 Phase 20.9: GitOps Readiness Audit for Sterling Sovereignty Stack"

# Check git folder
if [ ! -d .git ]; then
  echo "❌ Git folder missing. Run repo reset or clone manually."
  exit 1
fi

# Check remote origin
origin=$(git remote get-url origin 2>/dev/null || echo "")
if echo "$origin" | grep -q "jdorato376/sterling_ha_project"; then
  echo "✅ Correct origin set: $origin"
else
  echo "❌ Wrong origin: $origin"
  echo "    Use: git remote set-url origin https://github.com/jdorato376/sterling_ha_project"
  exit 1
fi

# Ensure core YAML files are tracked
for file in configuration.yaml intent_script.yaml automations.yaml; do
  if git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
    echo "✅ $file is Git-tracked."
  else
    echo "❌ $file not tracked in Git!"
    exit 1
  fi
done

# Validate agent directory
if [ ! -d custom_components/sterling ]; then
  echo "❌ Agent directory missing: /custom_components/sterling"
  exit 1
fi

grep -q "heartbeat" custom_components/sterling/* || echo "⚠️ No heartbeat references found. Add them before merge."

# Check secrets and memory files
if ! grep -q "platinum_dominion" secrets.yaml 2>/dev/null; then
  echo "⚠️ Governance block missing from secrets.yaml"
fi

for file in agent_dna_registry.json horizon_prediction.json verdict_ledger.yaml; do
  if [ ! -f config/storage/$file ]; then
    echo "❌ $file missing in /config/storage/"
    exit 1
  fi
  echo "✅ $file exists."
done

# Check Sovereign Mode intent_script
if grep -q "launch_sovereign_mode" configuration.yaml 2>/dev/null; then
  echo "✅ Sovereign Mode intent_script registered."
else
  echo "⚠️ Missing intent_script: launch_sovereign_mode"
fi

echo "\U1F4D8 Phase 20.9 validation complete."
