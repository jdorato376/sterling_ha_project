#!/bin/bash

set -e

HA_CONFIG_DIR="/config"
BACKUP_DIR="/config/backups/pre_sync"
LOG_FILE="/config/logs/gitops_sync.log"

HA_TOKEN="YOUR_HA_TOKEN"
HA_API_URL="http://localhost:8123/api"
GIT_BRANCH="main"

mkdir -p "$(dirname "$LOG_FILE")" "$BACKUP_DIR"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_message "Starting GitOps synchronization..."
cd "$HA_CONFIG_DIR" || { log_message "Error: Could not change to $HA_CONFIG_DIR"; exit 1; }

log_message "Creating Home Assistant backup via service..."
curl -X POST -H "Authorization: Bearer ${HA_TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{}' "${HA_API_URL}/services/backup/create" >>"$LOG_FILE" 2>&1 || \
    log_message "Warning: Backup service call failed. Continuing with git pull."

log_message "Fetching latest git commits..."
if ! git fetch origin >>"$LOG_FILE" 2>&1; then
    log_message "Error: git fetch failed."; exit 1
fi

log_message "Resetting to origin/${GIT_BRANCH}..."
if ! git reset --hard "origin/${GIT_BRANCH}" >>"$LOG_FILE" 2>&1; then
    log_message "Error: git reset failed."; exit 1
fi

log_message "Validating Home Assistant configuration..."
VALIDATION_OUTPUT=$(hass --script check_config -c "$HA_CONFIG_DIR" 2>&1)
if [ $? -eq 0 ]; then
    log_message "Config validation passed. Reloading core..."
    curl -X POST -H "Authorization: Bearer ${HA_TOKEN}" \
         -H "Content-Type: application/json" \
         -d '{}' "${HA_API_URL}/services/homeassistant/reload_core_config" >>"$LOG_FILE" 2>&1 || \
         log_message "Error: failed to reload core config."
    exit 0
else
    log_message "Config validation failed. Rolling back..."
    log_message "$VALIDATION_OUTPUT"
    git reset --hard HEAD@{1} >>"$LOG_FILE" 2>&1 || log_message "Rollback failed. Manual fix required."
    exit 1
fi
