#!/usr/bin/env bash
set -euo pipefail

# Sterling HA Recovery and Sentinel Test Script
# Restores repo if wiped and validates basic functionality

REPO_URL="${REPO_URL:-https://github.com/jdorato376/sterling_ha_project.git}"
HA_URL="${HA_URL:-https://your-ha-domain-or-ip}"
HA_TOKEN="${HA_TOKEN:-your_long_lived_token}"
OPENAI_API_KEY="${OPENAI_API_KEY:-your_codex_key}"
CONFIG_PATH="${CONFIG_PATH:-/config}"

# Restore repository if configuration is missing
if [ ! -f "$CONFIG_PATH/configuration.yaml" ]; then
  echo "📦 Restoring configuration from $REPO_URL"
  rm -rf "${CONFIG_PATH:?}"/*
  git clone "$REPO_URL" "$CONFIG_PATH"
fi

cd "$CONFIG_PATH"

echo "🔍 Sterling Sentinel Test Starting..."

# Step 1: Ping HA API
echo "🔧 Checking HA API reachability..."
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $HA_TOKEN" \
  "$HA_URL/api/")
if [ "$API_STATUS" = "200" ]; then
  echo "✅ HA API reachable"
else
  echo "❌ HA API unreachable ($API_STATUS)"
fi

# Step 2: Check configuration.yaml
if [ -f "$CONFIG_PATH/configuration.yaml" ]; then
  echo "✅ configuration.yaml exists"
else
  echo "❌ Missing configuration.yaml" && exit 1
fi

# Step 3: Canary entity check
ENTITY_CHECK=$(curl -s -H "Authorization: Bearer $HA_TOKEN" \
  "$HA_URL/api/states/input_boolean.canary_test" || true)
if [[ $ENTITY_CHECK == *"state"* ]]; then
  echo "✅ Canary entity found"
else
  echo "⚠️ Canary entity missing; adding to configuration.yaml"
  cat >> configuration.yaml <<'CANARY'
input_boolean:
  canary_test:
    name: Canary Test Toggle
    initial: off
    icon: mdi:shield-check
CANARY
fi

# Step 4: Toggle canary entity
curl -s -X POST "$HA_URL/api/services/input_boolean/toggle" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "input_boolean.canary_test"}' >/dev/null && \
  echo "✅ Toggle successful" || echo "❌ Toggle failed"

# Step 5: Test Codex write access
if echo "$OPENAI_API_KEY" | grep -q "sk-"; then
  npm install -g @openai/codex >/dev/null
  codex exec --full-auto "Append # Codex test pass to configuration.yaml" >/dev/null
  if grep -q "# Codex test pass" configuration.yaml; then
    echo "✅ Codex write succeeded"
  else
    echo "❌ Codex write failed"
  fi
else
  echo "❌ Invalid Codex key format" && exit 1
fi

# Step 6: Validate config syntax
echo "🧪 Validating Home Assistant config..."
if docker run -v "$CONFIG_PATH:/config" --rm \
  ghcr.io/home-assistant/home-assistant:stable --script check_config >/dev/null; then
  echo "✅ YAML validation passed"
else
  echo "❌ YAML validation failed"
fi

echo "✅ Sentinel test script completed."
