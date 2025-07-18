#!/usr/bin/env bash
# Stage 2: provision Home Assistant
set -euo pipefail

HA_IMAGE="homeassistant/home-assistant:stable"
CONTAINER_NAME="sterling-ha"
CONFIG_DIR="$(pwd)/config"
ADDONS_DIR="$(pwd)/addons"

# Ensure Sterling add-on exists
if [ ! -d "$ADDONS_DIR/sterling_os" ]; then
  echo "Sterling add-on missing; cloning repository..."
  tmpdir=$(mktemp -d)
  git clone https://github.com/jdorato376/sterling_ha_project "$tmpdir"
  mkdir -p "$ADDONS_DIR"
  cp -r "$tmpdir/addons/sterling_os" "$ADDONS_DIR/"
  rm -rf "$tmpdir"
fi

# Start Home Assistant container if not running
if ! docker ps -a --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
  docker run -d --name "$CONTAINER_NAME" \
    -v "$CONFIG_DIR":/config \
    -v "$ADDONS_DIR":/addons \
    -p 8123:8123 "$HA_IMAGE"
fi
if [ "$(docker inspect -f '{{.State.Running}}' $CONTAINER_NAME)" != "true" ]; then
  docker start "$CONTAINER_NAME"
fi

# Wait for Home Assistant API
until curl -sf http://localhost:8123/api/ >/dev/null; do
  echo "Waiting for Home Assistant API..."
  sleep 5
done

: "${HA_TOKEN:?HA_TOKEN must be set for Supervisor API}"
api() { curl -sS -H "Authorization: Bearer $HA_TOKEN" -H "Content-Type: application/json" "$@"; }

echo "Installing Sterling add-on..."
api -X POST http://localhost:8123/api/hassio/addons/sterling_os/install
api -X POST http://localhost:8123/api/hassio/addons/sterling_os/start

info=$(api http://localhost:8123/api/hassio/addons/sterling_os/info)
if echo "$info" | jq -e '.data.state == "started"' >/dev/null; then
  echo "✅ Stage 2: Home Assistant provisioned."
else
  echo "❌ Add-on failed to start" >&2
  exit 1
fi
