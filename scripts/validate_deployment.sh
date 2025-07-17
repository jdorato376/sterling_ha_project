#!/bin/bash
# validate_deployment.sh
# Simple sanity checks for a live Sterling Dominion deployment.
# Requires gcloud CLI and appropriate permissions.

set -euo pipefail

PROJECT_ID="${PROJECT_ID:?set PROJECT_ID}"
REGION="${REGION:-us-central1}"
CLOUD_RUN_SERVICE="${CLOUD_RUN_SERVICE:-ai-router}"
VM_NAME="${VM_NAME:-sterling-ha-vm}"
ZONE="${ZONE:-${REGION}-a}"

printf '\n=== Validating Cloud Run service ===\n'
RUN_URL=$(gcloud run services describe "$CLOUD_RUN_SERVICE" --region "$REGION" --format='value(status.url)')
if [ -n "$RUN_URL" ]; then
  echo "Cloud Run reachable at $RUN_URL"
else
  echo "Cloud Run service $CLOUD_RUN_SERVICE not found" && exit 1
fi

printf '\n=== Checking Compute Engine VM ===\n'
VM_STATUS=$(gcloud compute instances describe "$VM_NAME" --zone "$ZONE" --format='value(status)' 2>/dev/null || true)
if [ "$VM_STATUS" ]; then
  echo "VM $VM_NAME status: $VM_STATUS"
else
  echo "VM $VM_NAME not found" && exit 1
fi

printf '\n=== Checking Cloud SQL ===\n'
DB_NAME="${PROJECT_ID}-db"
DB_STATE=$(gcloud sql instances describe "$DB_NAME" --format='value(state)' 2>/dev/null || true)
if [ "$DB_STATE" ]; then
  echo "Cloud SQL instance $DB_NAME state: $DB_STATE"
else
  echo "Cloud SQL instance $DB_NAME not found" && exit 1
fi

printf '\n=== Checking Pub/Sub topic ===\n'
TOPIC_NAME="${PROJECT_ID}-events"
if gcloud pubsub topics describe "$TOPIC_NAME" >/dev/null 2>&1; then
  echo "Pub/Sub topic $TOPIC_NAME exists"
else
  echo "Pub/Sub topic $TOPIC_NAME not found" && exit 1
fi

echo "\nAll checks completed."
