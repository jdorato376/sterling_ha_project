#!/usr/bin/env bash
set -euo pipefail

# Vars
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}"
REGION="${REGION:-us-central1}"
REPO_OWNER="${REPO_OWNER:-jdorato376}"
REPO_NAME="${REPO_NAME:-sterling_ha_project}"
AR_REPO="sterling-ai-repo"
AR_LOCATION="$REGION"
IMAGE_URI="$AR_LOCATION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/sterling-ha:latest"
CLOUD_BUILD_CFG="cloudbuild.yaml"
TRIGGER_NAME="sterling-ha-trigger"
ENDPOINT_NAME="Sterling HA Endpoint"
HA_CONFIG="${HA_ADDON_CONFIG_PATH:-addons/sterling_os/config.json}"

# 1. Provision Artifact Registry
if ! gcloud artifacts repositories describe "$AR_REPO" --location="$AR_LOCATION" &>/dev/null; then
  gcloud artifacts repositories create "$AR_REPO" \
    --repository-format=docker \
    --location="$AR_LOCATION" \
    --description="Container registry for Sterling HA images"
fi

# 2. Enable Cloud Build
gcloud services enable cloudbuild.googleapis.com --project="$PROJECT_ID"

# 3. Build & Push via Cloud Build
gcloud builds submit --project="$PROJECT_ID" --config="$CLOUD_BUILD_CFG" \
  --substitutions=_REGION="$REGION",_REPO="$REPO_NAME"

# 4. Create/Update Cloud Build Trigger
if gcloud builds triggers list --project="$PROJECT_ID" --filter="name:$TRIGGER_NAME" --format="value(name)" | grep -q "$TRIGGER_NAME"; then
  gcloud builds triggers update "$TRIGGER_NAME" --project="$PROJECT_ID" \
    --repo-owner="$REPO_OWNER" \
    --repo-name="$REPO_NAME" \
    --branch-pattern="^main$" \
    --build-config="$CLOUD_BUILD_CFG"
else
  gcloud builds triggers create github --project="$PROJECT_ID" \
    --name="$TRIGGER_NAME" \
    --repo-owner="$REPO_OWNER" \
    --repo-name="$REPO_NAME" \
    --branch-pattern="^main$" \
    --build-config="$CLOUD_BUILD_CFG"
fi

# 5. Create or reuse Vertex AI Endpoint
ENDPOINT_ID=$(gcloud ai endpoints list --region="$REGION" --filter="displayName=$ENDPOINT_NAME" --format="value(name)" 2>/dev/null || true)
if [ -z "$ENDPOINT_ID" ]; then
  echo "ℹ️ Endpoint '$ENDPOINT_NAME' not found. Creating..."
  ENDPOINT_ID=$(gcloud ai endpoints create --region="$REGION" \
    --display-name="$ENDPOINT_NAME" \
    --format="value(name)")
else
  echo "ℹ️ Using existing endpoint $ENDPOINT_ID"
fi

# 6. Deploy Model Container to Endpoint
gcloud ai endpoints deploy-model "$ENDPOINT_ID" \
  --region="$REGION" \
  --model="$IMAGE_URI" \
  --display-name="sterling-ha-$(date +%Y%m%d%H%M%S)" \
  --traffic-split=0=100 \
  --machine-type="n1-standard-2"

# 7. Update Home Assistant Add-on Config
if [ -f "$HA_CONFIG" ]; then
  jq --arg img "$IMAGE_URI" '.image = $img' "$HA_CONFIG" > tmp.$$.json && mv tmp.$$.json "$HA_CONFIG"
  git add "$HA_CONFIG"
  git commit -m "chore: update HA add-on image → $IMAGE_URI"
else
  echo "⚠️ HA config not found at '$HA_CONFIG'"
fi

# 8. Push Changes
git push origin main

echo "✅ Stage 1: Vertex deploy complete."
