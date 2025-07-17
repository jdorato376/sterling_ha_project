#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-your-project-id}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="ai-router"

IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

# Build container image

gcloud builds submit --tag "$IMAGE"

# Deploy to Cloud Run

gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated
