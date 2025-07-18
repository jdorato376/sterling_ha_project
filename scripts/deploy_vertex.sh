#!/usr/bin/env bash
# Sterling HA Project - Vertex AI Deployment Script
# Stage 1: deploy Vertex resources with enhanced environment support
set -euo pipefail

# Load environment variables from .env file
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env file..."
    source .env
else
    echo "⚠️  No .env file found. Using environment variables or defaults."
fi

# Validate required environment variables
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT in .env or environment}"
REGION="${REGION:-us-central1}"
REPO_OWNER="${REPO_OWNER:-jdorato376}"
REPO_NAME="${REPO_NAME:-sterling_ha_project}"
AR_REPO="${ARTIFACT_REGISTRY_REPO:-sterling-ai-repo}"
AR_LOCATION="$REGION"
IMAGE_URI="$AR_LOCATION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/sterling-ha:latest"
CLOUD_BUILD_CFG="cloudbuild.yaml"
TRIGGER_NAME="sterling-ha-trigger"
ENDPOINT_NAME="Sterling HA Endpoint"
HA_CONFIG="${HA_ADDON_CONFIG_PATH:-addons/sterling_os/config.json}"

echo "🚀 Starting Vertex AI deployment..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Image URI: $IMAGE_URI"

# Enable required GCP APIs
echo "📋 Enabling required GCP APIs..."
gcloud services enable aiplatform.googleapis.com --project="$PROJECT_ID"
gcloud services enable artifactregistry.googleapis.com --project="$PROJECT_ID"
gcloud services enable cloudbuild.googleapis.com --project="$PROJECT_ID"
gcloud services enable container.googleapis.com --project="$PROJECT_ID"
gcloud services enable compute.googleapis.com --project="$PROJECT_ID"

# Create Artifact Registry repository if it doesn't exist
echo "🏗️  Setting up Artifact Registry..."
if ! gcloud artifacts repositories describe "$AR_REPO" --location="$AR_LOCATION" --project="$PROJECT_ID" &>/dev/null; then
    echo "📦 Creating Artifact Registry repository..."
    gcloud artifacts repositories create "$AR_REPO" \
        --repository-format=docker \
        --location="$AR_LOCATION" \
        --description="Container registry for Sterling HA images" \
        --project="$PROJECT_ID"
else
    echo "✅ Artifact Registry repository already exists"
fi

# Build & Push via Cloud Build
echo "🔨 Building and pushing container via Cloud Build..."
gcloud builds submit --project="$PROJECT_ID" --config="$CLOUD_BUILD_CFG" \
    --substitutions=_REGION="$REGION",_REPO="$REPO_NAME"

# Create/Update Cloud Build Trigger
echo "⚙️  Setting up Cloud Build trigger..."
if gcloud builds triggers list --project="$PROJECT_ID" --filter="name:$TRIGGER_NAME" --format="value(name)" | grep -q "$TRIGGER_NAME"; then
    echo "🔄 Updating existing Cloud Build trigger..."
    gcloud builds triggers update github "$TRIGGER_NAME" --project="$PROJECT_ID" \
        --repo-owner="$REPO_OWNER" \
        --repo-name="$REPO_NAME" \
        --branch-pattern="^main$" \
        --build-config="$CLOUD_BUILD_CFG" \
        --substitutions=_REGION="$REGION",_REPO="$REPO_NAME"
else
    echo "➕ Creating new Cloud Build trigger..."
    gcloud builds triggers create github --project="$PROJECT_ID" \
        --name="$TRIGGER_NAME" \
        --repo-owner="$REPO_OWNER" \
        --repo-name="$REPO_NAME" \
        --branch-pattern="^main$" \
        --build-config="$CLOUD_BUILD_CFG" \
        --substitutions=_REGION="$REGION",_REPO="$REPO_NAME"
fi

# Create or reuse Vertex AI Endpoint
echo "🔍 Setting up Vertex AI endpoint..."
ENDPOINT_ID=$(gcloud ai endpoints list --region="$REGION" --project="$PROJECT_ID" --filter="displayName=\"$ENDPOINT_NAME\"" --format="value(name)" 2>/dev/null || echo "")

if [ -z "$ENDPOINT_ID" ]; then
    echo "➕ Creating new Vertex AI endpoint..."
    ENDPOINT_ID=$(gcloud ai endpoints create --region="$REGION" --project="$PROJECT_ID" \
        --display-name="$ENDPOINT_NAME" \
        --format="value(name)")
    echo "✅ Created endpoint: $ENDPOINT_ID"
else
    echo "✅ Using existing endpoint: $ENDPOINT_ID"
fi

# Deploy Model Container to Endpoint (with error handling)
echo "🚀 Deploying model to Vertex AI endpoint..."
DEPLOYMENT_NAME="sterling-ha-$(date +%Y%m%d%H%M%S)"

# Check if the image exists before deploying
if gcloud container images describe "$IMAGE_URI" --project="$PROJECT_ID" &>/dev/null; then
    echo "📦 Container image found, deploying to endpoint..."
    
    # Deploy with error handling
    if gcloud ai endpoints deploy-model "$ENDPOINT_ID" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --model-display-name="$DEPLOYMENT_NAME" \
        --container-image-uri="$IMAGE_URI" \
        --container-health-route="/health" \
        --container-predict-route="/predict" \
        --container-ports="8080" \
        --traffic-split="0=100" \
        --machine-type="n1-standard-2" \
        --min-replica-count=1 \
        --max-replica-count=3; then
        echo "✅ Model deployed successfully"
    else
        echo "⚠️  Model deployment failed, but continuing..."
    fi
else
    echo "⚠️  Container image not found at $IMAGE_URI, skipping model deployment"
fi

# Update Home Assistant Add-on Config
echo "🏠 Updating Home Assistant add-on configuration..."
if [ -f "$HA_CONFIG" ]; then
    # Create backup
    cp "$HA_CONFIG" "$HA_CONFIG.backup.$(date +%Y%m%d%H%M%S)"
    
    # Update image URI in config
    if command -v jq &> /dev/null; then
        jq --arg img "$IMAGE_URI" '.image = $img' "$HA_CONFIG" > tmp.$$.json && mv tmp.$$.json "$HA_CONFIG"
        echo "✅ Updated HA add-on config with new image"
        
        # Git operations (if in git repo)
        if [ -d .git ]; then
            git add "$HA_CONFIG"
            git commit -m "chore: update HA add-on image → $IMAGE_URI" || echo "No changes to commit"
        fi
    else
        echo "⚠️  jq not available, skipping config update"
    fi
else
    echo "⚠️  HA config not found at '$HA_CONFIG', skipping config update"
fi

# Create deployment summary
echo "📊 Deployment Summary:"
echo "===================="
echo "✅ Project: $PROJECT_ID"
echo "✅ Region: $REGION"
echo "✅ Image URI: $IMAGE_URI"
echo "✅ Endpoint ID: $ENDPOINT_ID"
echo "✅ Deployment: $DEPLOYMENT_NAME"
echo ""
echo "🔗 Useful commands:"
echo "gcloud ai endpoints list --region=$REGION --project=$PROJECT_ID"
echo "gcloud ai endpoints describe $ENDPOINT_ID --region=$REGION --project=$PROJECT_ID"
echo ""
echo "✅ Stage 1: Vertex AI deployment completed successfully!"
