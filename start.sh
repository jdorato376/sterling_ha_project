#!/bin/bash

# Sterling Sentinel Test Script

# Display startup message
echo "🔍 Sterling Sentinel Test Starting..."

# --- SET THESE VARIABLES ---
HA_URL="https://your-ha-domain-or-ip"
HA_TOKEN="your_long_lived_token"
OPENAI_API_KEY="your_codex_key"
CONFIG_PATH="/config"

# --- Step 1: Ping HA API ---
echo "🔧 Checking HA API reachability..."
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $HA_TOKEN" \
  "$HA_URL/api/")
if [ "$API_STATUS" = "200" ]; then
  echo "✅ HA API reachable"
else
  echo "❌ HA API unreachable ($API_STATUS)"
fi

# --- Step 2: Check config file ---
echo "🧾 Checking configuration.yaml..."
if [ -f "$CONFIG_PATH/configuration.yaml" ]; then
  echo "✅ configuration.yaml exists"
else
  echo "❌ Missing configuration.yaml"
fi

# --- Step 3: Check canary entity exists ---
echo "🔍 Checking for input_boolean.canary_test..."
ENTITY_CHECK=$(curl -s -H "Authorization: Bearer $HA_TOKEN" \
  "$HA_URL/api/states/input_boolean.canary_test")
if [[ $ENTITY_CHECK == *"state"* ]]; then
  echo "✅ Canary entity found"
else
  echo "❌ Canary entity NOT found — consider adding to YAML"
fi

# --- Step 4: Try to toggle it ---
echo "🟡 Toggling input_boolean.canary_test..."
curl -s -X POST "$HA_URL/api/services/input_boolean/toggle" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "input_boolean.canary_test"}' > /dev/null && \
  echo "✅ Toggle successful" || echo "❌ Toggle failed"

# --- Step 5: Test Codex write ---
echo "🧠 Testing Codex CLI write to $CONFIG_PATH..."
if echo "$OPENAI_API_KEY" | grep -q "sk-"; then
  npm install -g @openai/codex
  cd "$CONFIG_PATH"
  codex exec --full-auto "Append # Codex test pass to configuration.yaml" && \
  grep "# Codex test pass" configuration.yaml > /dev/null && \
  echo "✅ Codex write succeeded" || echo "❌ Codex write failed"
else
  echo "❌ Invalid Codex key format"
  exit 1
fi

# --- Step 6: Validate config syntax ---
echo "🧪 Validating Home Assistant config..."
docker run -v "$CONFIG_PATH:/config" --rm \
  ghcr.io/home-assistant/home-assistant:stable --script check_config && \
  echo "✅ YAML validation passed" || echo "❌ YAML validation failed"

echo "✅ Sentinel test script completed."
