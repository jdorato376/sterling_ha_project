#!/usr/bin/env bash
# Phase 5: Emergency Override & Fail-Safe Rollbacks
set -euo pipefail

echo "\xF0\x9F\x9A\xA8 Initiating Sterling Phase 5 \xE2\x80\x94 Emergency Override Protocols"
cd /config || { echo "\xE2\x9D\x8C ERROR: Cannot access /config"; exit 1; }

# Capture rollback point
git rev-parse HEAD > .last_successful_commit
printf "\xF0\x9F\x93\x9D Current commit saved: %s\n" "$(cat .last_successful_commit)"

# Validate configuration
if ! docker run -v "$PWD:/config" --rm ghcr.io/home-assistant/home-assistant:stable --script check_config; then
  echo "\xE2\x9D\x8C CONFIG VALIDATION FAILED"
  echo "\xF0\x9F\x94\x81 Rolling back to last known good commit..."
  git reset --hard "$(cat .last_successful_commit)"
  ha core restart
  echo "\xE2\x9C\x85 Rolled back and HA restarted"
  exit 1
fi

# Create rollback trigger entity if missing
if ! grep -q "input_boolean.rollback_trigger" configuration.yaml; then
  cat <<'YAML' >> configuration.yaml

input_boolean:
  rollback_trigger:
    name: Emergency Rollback
    initial: off
    icon: mdi:restart-alert
YAML
fi

# Reload configuration to register entity
curl -s -X POST \
  -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' http://homeassistant.local:8123/api/services/homeassistant/reload_core_config

# Create watchdog script
cat <<'SH' > /config/sentinel_watchdog.sh
#!/bin/bash
STATE=$(curl -s -H "Authorization: Bearer $HA_LONG_LIVED_TOKEN" \
  http://homeassistant.local:8123/api/states/input_boolean.rollback_trigger | jq -r '.state')

if [ "$STATE" = "on" ]; then
  echo "\xE2\x9A\xA0\xEF\xB8\x8F Rollback triggered by user \xE2\x80\x94 executing fail-safe"
  git reset --hard "$(cat /config/.last_successful_commit)"
  ha core restart
  echo "\xE2\x9C\x85 System reverted to stable state"
fi
SH
chmod +x /config/sentinel_watchdog.sh

# Schedule watchdog
(crontab -l 2>/dev/null; echo "* * * * * /config/sentinel_watchdog.sh") | crontab -

echo "\xF0\x9F\x93\xA1 Phase 5 setup complete: Emergency override protocols active"
