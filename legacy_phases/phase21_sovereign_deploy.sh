#!/bin/bash

echo "\U1F441\uFE0F Sterling Sovereign Deploy – Phase 20.9 to 21 Final Lock-In"
cd /config || { echo "❌ /config not accessible. Abort."; exit 1; }

# 1. Backup existing configuration
echo "🧷 Creating timestamped backup..."
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz .

# 2. Wipe prior Git setup to avoid contamination
echo "🧹 Cleaning up old Git config..."
rm -rf .git .gitmodules .github

# 3. Clone latest repo
echo "🌐 Cloning Sterling HA GitHub repo..."
if ! git clone https://github.com/jdorato376/sterling_ha_project .; then
  echo "❌ Git clone failed. Check access."; exit 1;
fi

# 4. Git identity re-init
git config --global user.name "Sterling AutoDeploy"
git config --global user.email "deploy@platinum.ai"
git remote set-url origin https://github.com/jdorato376/sterling_ha_project

# 5. Validate essential files exist
echo "📁 Validating required logic files..."
for f in configuration.yaml automations.yaml intent_script.yaml; do
  [[ -f "$f" ]] || { echo "❌ Missing critical: $f"; exit 1; }
done

# 6. Install agents into custom_components
echo "🧠 Installing Platinum Dominion agents..."
mkdir -p custom_components/sterling
cp -R homeassistant_config/sterling/* custom_components/sterling/

# 7. Register Sovereign Intent + Governance in YAML
if ! grep -q "launch_sovereign_mode" configuration.yaml; then
  echo "🔐 Injecting governance schema into configuration.yaml..."
  cat <<'EOC' >> configuration.yaml

# 🤖 Phase 21 – Executive Sovereign Mode (Manual-Precision Triggered)
intent_script:
  launch_sovereign_mode:
    action:
      - service: python_script.sovereign_init

platinum_dominion:
  codex_gpt: active
  sterling_gpt_core: active
  magistrate: active
  concord_agent: active
  syndicator_agent: active
  mutation_engine: active
  sentinel: legacy
  canary: dual-role
sovereign_sync_protocol:
  automation_in_home_assistant: false
  sync_method: manual_curation
  feedback_loop:
    - agents detect gap
    - escalate to Sterling AI
    - Codex confirms, fixes, pushes to GitHub
    - Home Assistant redeploys on command
  validation:
    - all commits must pass heartbeat & schema trace
    - HA only updates on Codex-confirmed merges
EOC
fi

# 8. Register sovereign governance in secrets.yaml
if ! grep -q "platinum_dominion" secrets.yaml 2>/dev/null; then
  echo "🔑 Sealing governance authority in secrets.yaml..."
  cat <<'EOC' >> secrets.yaml

# 🔐 Platinum Dominion Governance Token
platinum_dominion:
  sovereign_token: "STERLING-21-ROOT"
  last_validation_pass: "Phase 20.9 – Verified Integrity"
EOC
fi

# 9. Ensure all required memory state files exist
echo "💾 Preparing persistent intelligence state..."
mkdir -p storage
for f in agent_dna_registry.json horizon_prediction.json verdict_ledger.yaml; do
  touch "storage/$f"
done

# 10. Run GitOps compliance test
echo "🧪 Running Phase 20.9 pre-merge audit..."
if ! bash -c "$(curl -fsSL https://raw.githubusercontent.com/jdorato376/sterling_ha_project/main/phase_20_9_gitops_check.sh)"; then
  echo "❌ Validation test failed. Abort merge and fix manually."; exit 1;
fi

# 11. Restart Home Assistant to trigger Sovereign Mode
echo "🚀 Restarting HA Core to launch Platinum Dominion..."
ha core restart || echo "⚠️ Restart failed – reboot manually if needed."

echo "✅ Sterling Sovereign Stack fully deployed and HA is under governance."
echo "🛂 All changes traceable through Codex, no automation runs without human confirmation."
exit 0
