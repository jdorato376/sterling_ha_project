#!/usr/bin/env bash
set -euo pipefail
# Phase 191: Provision a cost-friendly GCP VM with HA-Optimized OS
gcloud compute instances create sterling-ha-vm \
  --project="$GOOGLE_CLOUD_PROJECT" \
  --zone="$REGION-a" \
  --machine-type=f1-micro \
  --image-family=homeassistant-os-odroid-c4 \
  --image-project=home-assistant-io \
  --boot-disk-size=20GB \
  --tags=http-server,https-server
