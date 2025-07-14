#!/bin/bash

set -e

# Activate virtual environment if available
if [ -f venv/bin/activate ]; then
  source venv/bin/activate
fi

cd "$(dirname "$0")"

# Ensure diagnostics exist
mkdir -p addons/sterling_os/logs addons/sterling_os/trust results

touch addons/sterling_os/logs/audit_log.json
: > addons/sterling_os/trust/trust_registry.json
: > addons/sterling_os/predictive_recovery.json
: > addons/sterling_os/scene_trace.json


echo "[PHASE 40.9] BEGINNING SYNTHETIC SYSTEM HEALTH TEST..."

pytest -v \
  tests/test_agent_rotation_phase10.py \
  tests/test_self_healing_and_predictive_trust.py \
  tests/test_escalation_engine.py \
  tests/test_runtime_memory.py \
  tests/test_cognitive_router.py \
  tests/test_resilience_engine.py \
  tests/test_heartbeat.py \
  tests/test_smart_router.py \
  tests/test_autonomy.py \
  tests/test_memory_conflict.py \
  | tee results/phase_40_9_synthetic_validation.log

cat <<'MSG'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Synthetic E2E Health Validation COMPLETE
📄 Full log saved to: results/phase_40_9_synthetic_validation.log
📜 Audit Log: addons/sterling_os/logs/audit_log.json
🧠 Trust Registry: addons/sterling_os/trust/trust_registry.json
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MSG

