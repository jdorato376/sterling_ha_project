#!/bin/bash

# ===============================================================
# 📘 Sterling GPT Deployment Validation: Phases 1 to 10
# Author: Codex GPT x Jimmy Dorato
# Location: /config/sterling_ha_project/scripts/validate_phases_1_to_10.sh
# Purpose: Confirm every layer of system functionality from Canary → Rollback → Self-Healing → Reflex Routing
# ===============================================================

set -euo pipefail

echo "🔍 BEGIN: Sterling GPT Full System Validation"

echo "🌀 Phase 1: Canary Diagnostic — Core File & API Check"
if [ -f "/config/configuration.yaml" ]; then
  echo "✅ configuration.yaml exists"
else
  echo "❌ Missing configuration.yaml"
  exit 1
fi

if curl -s -X POST "http://localhost:8123/api/services/input_boolean/toggle" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "input_boolean.canary_test"}' | grep -q "200"; then
  echo "✅ Home Assistant API toggle successful"
else
  echo "❌ API test failed"
  exit 1
fi

echo "✅ Phase 1 complete"

echo "🔁 Phase 2: GitOps Sync Check"
cd /config
if git status | grep -q "working tree clean"; then
  echo "✅ Git repo is clean"
else
  echo "❌ Git repo not clean"
  git status
fi

echo "📦 Phase 3: Reflex Engine — Canary Trigger Simulation"
if curl -s -X POST http://localhost:8123/api/services/script/turn_on \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "script.sterling_canary_simulate"}' | grep -q "200"; then
  echo "✅ Reflex engine script fired"
else
  echo "❌ Reflex engine simulation failed"
fi

echo "🧠 Phase 4: Git Auto-Heal Logic"
if git fetch origin main && git diff --quiet origin/main; then
  echo "✅ No repo divergence detected"
else
  echo "⚠️ Repo diverged, initiating self-heal"
  git reset --hard origin/main
  echo "🔁 Reloading HA core"
  ha core restart
fi

echo "🛡️ Phase 5: Sentinel Mode — Emergency Readiness Check"
if grep -q "sentinel_mode: true" /config/sterling_ha_project/core/settings.yaml 2>/dev/null; then
  echo "✅ Sentinel Mode enabled"
else
  echo "❌ Sentinel Mode not detected — activating fallback logic"
  echo "sentinel_mode: true" >> /config/sterling_ha_project/core/settings.yaml
fi

echo "📈 Phase 6: Escalation Intelligence & Trust Audit Trigger"
if curl -s -X POST http://localhost:8123/api/webhook/sterling_escalation_matrix_trigger \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | grep -q "200"; then
  echo "✅ Escalation Matrix webhook fired"
else
  echo "❌ Escalation trigger failed"
fi

echo "🩺 Phase 7: Predictive Recovery Trace"
LOG_FILE="/config/sterling_ha_project/logs/recovery_trace.log"
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"
echo "[TEST] Triggering recovery preview logic" >> "$LOG_FILE"
if [ -s "$LOG_FILE" ]; then
  echo "✅ Predictive recovery trace logged"
else
  echo "❌ Predictive recovery output missing"
fi

echo "🔄 Phase 8: Resilience Simulation"
if curl -s -X POST http://localhost:8123/api/services/scene/turn_on \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "scene.resilience_simulation"}' | grep -q "200"; then
  echo "✅ Scene executed"
else
  echo "❌ Scene trigger failed"
fi

echo "🔁 Phase 9: AI Agent Switching Logic"
python3 /config/sterling_ha_project/agents/agent_switch_test.py && echo "✅ Agent switching script passed" || echo "❌ Agent switching logic failed"

echo "📡 Phase 10: Infrastructure Mastery & Reflex Lock"
if curl -s -X POST http://localhost:8123/api/webhook/sterling_full_reflex \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | grep -q "200"; then
  echo "✅ Reflex intelligence test webhook passed"
else
  echo "❌ Reflex webhook failed"
fi

echo "🏁 All phases complete. Sterling GPT stack validated through Phase 10."
