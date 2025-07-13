#!/usr/bin/env bash
# === Sterling GPT Executive Sentinel Deployment ===
# Version: 3.0 — Built by Codex GPT for Jimmy Dorato
# Last Updated: July 13, 2025
# Scope: Full HAOS initialization, GitOps setup, Sentinel Mode activation

set -euo pipefail

# ⛔ PRECONDITION: GitHub, SSH, and Home Assistant CLI must be available.
# Environment variables may be sourced from a secret manager:
#   HA_LONG_LIVED_TOKEN - Home Assistant token
#   HA_URL              - Home Assistant base URL
#   GITHUB_REPO         - Git repository with Sterling configuration
#   GITHUB_BRANCH       - Branch to checkout

: "${HA_LONG_LIVED_TOKEN:?Must export HA_LONG_LIVED_TOKEN}"
: "${HA_URL:?Must export HA_URL}"
: "${GITHUB_REPO:?Must export GITHUB_REPO}"
: "${GITHUB_BRANCH:?Must export GITHUB_BRANCH}"

########################################
# Step 1: prepare config directory
########################################
command -v ha >/dev/null 2>&1 || { echo "❌ HA CLI not found"; exit 1; }
cd /config || { echo "❌ Failed to cd /config"; exit 1; }

########################################
# Step 2: wipe old files
########################################
ha core stop || echo "⚠️ Home Assistant core already stopped"
rm -rf /config/.git
rm -rf /config/custom_components/sterling*
rm -rf /config/sterling_ha_project
rm -rf /config/old_* /config/backup_* /config/tmp_*
rm -f /config/*.log /config/home-assistant_v2.db

########################################
# Step 3: clone repo fresh
########################################
git clone "$GITHUB_REPO" --branch "$GITHUB_BRANCH" sterling_ha_project

########################################
# Step 4: install component and configs
########################################
mkdir -p /config/custom_components
cp -r sterling_ha_project/homeassistant_config/custom_components/sterling /config/custom_components/sterling
chmod -R 755 /config/custom_components/sterling
cp -n sterling_ha_project/homeassistant_config/configuration.yaml /config/
cp -n sterling_ha_project/homeassistant_config/secrets.yaml /config/
cp -n sterling_ha_project/homeassistant_config/automations.yaml /config/
cp -n sterling_ha_project/homeassistant_config/scripts.yaml /config/

########################################
# Step 5: initialize Git for sync
########################################
cd /config
if [ ! -d .git ]; then
  git init
  git remote add origin "$GITHUB_REPO"
fi
git fetch origin
git checkout -f "$GITHUB_BRANCH" || git checkout -b "$GITHUB_BRANCH"
git reset --hard "origin/$GITHUB_BRANCH"

########################################
# Step 6: start Home Assistant
########################################
ha core start
sleep 20

########################################
# Step 7: inject canary entity
########################################
if ! grep -q "canary_test" configuration.yaml; then
  cat >> configuration.yaml <<'YAML'
input_boolean:
  canary_test:
    name: Canary Test Toggle
    initial: off
    icon: mdi:shield-check
YAML
fi

curl -s -X POST "$HA_URL/api/services/homeassistant/reload_core_config" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" \
  -H "Content-Type: application/json" -d '{}' || echo "⚠️ reload_core_config failed"

curl -s -X POST "$HA_URL/api/services/input_boolean/toggle" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "input_boolean.canary_test"}'

########################################
# Step 8: validate config
########################################
docker run -v "$PWD:/config" --rm ghcr.io/home-assistant/home-assistant:stable --script check_config

########################################
# Step 9: Sentinel webhook setup
########################################
WEBHOOK_CODE=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 16)
cat >> automations.yaml <<EOF_A
# === Sentinel Canary Webhook Automation ===
- alias: 'Sterling Sentinel Canary Trigger'
  trigger:
    - platform: webhook
      webhook_id: 'sterling_sentinel_${WEBHOOK_CODE}'
  action:
    - service: shell_command.sentinel_cleanup
    - service: notify.persistent_notification
      data:
        title: 'Sterling Sentinel'
        message: 'Webhook cleanup triggered by GitOps pipeline.'
EOF_A

########################################
# Step 10: cleanup script
########################################
mkdir -p scripts
cat <<'EOF_B' > scripts/sentinel_cleanup.sh
#!/usr/bin/env bash
cd /config
echo '🧠 Sentinel cleanup: recloning repo and restarting HA...'
rm -rf custom_components/sterling*
git fetch origin
git reset --hard origin/main
ha core restart
EOF_B
chmod +x scripts/sentinel_cleanup.sh

########################################
# Step 11: add shell command
########################################
cat >> configuration.yaml <<'EOF_C'
shell_command:
  sentinel_cleanup: '/config/scripts/sentinel_cleanup.sh'
EOF_C

curl -s -X POST "$HA_URL/api/services/homeassistant/reload_core_config" \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" \
  -H "Content-Type: application/json" -d '{}' || echo "⚠️ reload_core_config failed"

########################################
# Step 12: optional GitHub pull automation
########################################
cat <<'EOF_D' >> automations.yaml
- alias: 'Sterling GitHub Pull Trigger'
  trigger:
    platform: webhook
    webhook_id: sterling_git_sync
  action:
    - service: hassio.addon_start
      data:
        addon: "core_git_pull"
    - delay: 30
    - service: homeassistant.restart
EOF_D

########################################
# Step 13: final message
########################################
echo "✅ Sterling is fully deployed with Sentinel Mode enabled." 
echo "🔐 Sentinel Webhook: POST to → $HA_URL/api/webhook/sterling_sentinel_${WEBHOOK_CODE}"
echo "🛡️ Canary toggled and configuration validated"
echo "📣 Trigger git sync via webhook /api/webhook/sterling_git_sync"
