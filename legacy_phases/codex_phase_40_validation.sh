#!/bin/bash

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔁 Checking out Codex Phase 40"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

git checkout codex_phase_40 && git pull origin codex_phase_40

echo "🧼 Cleaning + Touching Diagnostic Files..."
mkdir -p addons/sterling_os/logs addons/sterling_os/trust
> addons/sterling_os/audit_log.json
echo '{}' > addons/sterling_os/trust/trust_registry.json
> addons/sterling_os/scene_trace.json
> addons/sterling_os/predictive_recovery.json

echo "🧪 Running Targeted Test Suite..."
pytest -q \
  tests/test_cognitive_router.py \
  tests/test_self_healing_and_predictive_trust.py \
  tests/test_resilience_engine.py \
  tests/test_escalation_engine.py \
  tests/test_agent_rotation_phase10.py \
  tests/test_memory_conflict.py \
  tests/test_heartbeat.py \
  tests/test_runtime_memory.py \
  tests/test_schema_escalator.py \
  tests/test_routes.py

echo "🔁 Running GitOps Sync..."
python3 -m addons.sterling_os.ha_gitops_sync

echo "📜 Displaying Last 25 Lines of Audit Log..."
tail -n 25 addons/sterling_os/logs/audit_log.json

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Codex Phase 40.9 VALIDATION COMPLETE"
echo "📜 Logs: addons/sterling_os/logs/audit_log.json"
echo "🧠 Trust: addons/sterling_os/trust/trust_registry.json"
echo "🔁 Recovery: addons/sterling_os/predictive_recovery.json"
echo "📂 Scene Trace: addons/sterling_os/scene_trace.json"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
