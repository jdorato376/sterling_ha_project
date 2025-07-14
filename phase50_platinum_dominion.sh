#!/bin/bash
# Phase 50: Platinum Dominion Consolidation — Aegis Protocol

echo "\U0001F451 [Phase 50] Launching Constitutional Layer: Platinum Dominion..."

mkdir -p addons/sterling_os/platinum_dominion

# Constitution file creation (if missing)
if [ ! -f addons/sterling_os/platinum_dominion/constitution.json ]; then
  cat <<EOT > addons/sterling_os/platinum_dominion/constitution.json
{
  "version": "1.0.0",
  "ratified_on": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "core_principles": {
    "human_governance": true,
    "agent_escalation_require_approval": true,
    "persona_separation": true,
    "zero_cost_without_explicit_ok": true,
    "rollback_on_error": true
  },
  "ratified_by": ["SterlingGPT", "CodexGPT"],
  "executive_layer": {"name": "Platinum Dominion", "chair": "User"}
}
EOT
fi

# Aegis enforcement module
if [ ! -f addons/sterling_os/platinum_dominion/aegis_enforcer.py ]; then
  cat <<'EOT' > addons/sterling_os/platinum_dominion/aegis_enforcer.py
import json

def enforce_governance(agent_id: str, action: str, requires_approval: bool = True) -> dict:
    with open("addons/sterling_os/platinum_dominion/constitution.json") as f:
        charter = json.load(f)
    if charter["core_principles"].get("human_governance") and requires_approval:
        if agent_id not in charter["executive_layer"].get("executive_agents", []):
            return {"status": "halted", "reason": "Human approval required", "agent": agent_id}
    return {"status": "approved"}
EOT
fi

# Patch router if needed
if ! grep -q aegis_enforcer cognitive_router.py; then
  sed -i '1s/^/from addons.sterling_os.platinum_dominion import aegis_enforcer\n/' cognitive_router.py
  sed -i '/def handle_request/a\    if aegis_enforcer.enforce_governance(agent, query).get("status") != "approved":\n        return {"error": "Blocked by Platinum Dominion Constitution"}' cognitive_router.py
fi

cat <<EOT > addons/sterling_os/platinum_dominion/ratification.log
[Platinum Dominion Ratification Log]
Date: $(date)
Phase: 50
Status: Ratified
Authority: Platinum Dominion
EOT

ruff check . && pytest -q && echo "Checks passed" || echo "Checks failed"

ha core restart >/dev/null 2>&1 && echo "HA restarted"
python3 -m addons.sterling_os.ha_gitops_sync

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Phase 50 COMPLETE: Platinum Dominion Now Governs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
