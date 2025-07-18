#!/usr/bin/env bash
# Sterling HA Vertex AI Deployment Script
# Enhanced with .env support and comprehensive API enablement
set -euo pipefail

# Load environment variables from .env if it exists
if [ -f ".env" ]; then
    echo "📝 Loading environment variables from .env..."
    # shellcheck disable=SC1091
    source .env
fi

# Variables with defaults
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT in .env}"
REGION="${REGION:-us-central1}"
REPO_OWNER="${REPO_OWNER:-jdorato376}"
REPO_NAME="${REPO_NAME:-sterling_ha_project}"
AR_REPO="${ARTIFACT_REGISTRY_REPO:-sterling-ha-repo}"
AR_LOCATION="$REGION"
IMAGE_URI="$AR_LOCATION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/sterling-ha:latest"
CLOUD_BUILD_CFG="cloudbuild.yaml"
TRIGGER_NAME="${CLOUD_BUILD_TRIGGER_NAME:-sterling-ha-trigger}"
ENDPOINT_NAME="${VERTEX_AI_ENDPOINT_NAME:-Sterling HA Endpoint}"
HA_CONFIG="${HA_ADDON_CONFIG_PATH:-addons/sterling_os/config.json}"

echo "🚀 Starting Sterling HA Vertex AI deployment..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Artifact Registry: $AR_REPO"

# 1. Enable required APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable \
    compute.googleapis.com \
    aiplatform.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    bigquery.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    cloudresourcemanager.googleapis.com \
    --project="$PROJECT_ID"

# Wait for APIs to be fully enabled
echo "⏳ Waiting for APIs to be fully enabled..."
sleep 30

# 2. Provision Artifact Registry
echo "📦 Setting up Artifact Registry..."
if ! gcloud artifacts repositories describe "$AR_REPO" --location="$AR_LOCATION" --project="$PROJECT_ID" &>/dev/null; then
    gcloud artifacts repositories create "$AR_REPO" \
        --repository-format=docker \
        --location="$AR_LOCATION" \
        --description="Container registry for Sterling HA images" \
        --project="$PROJECT_ID"
    echo "✅ Created Artifact Registry repository: $AR_REPO"
else
    echo "✅ Artifact Registry repository already exists: $AR_REPO"
fi

# 3. Configure Docker authentication
echo "🔑 Configuring Docker authentication..."
gcloud auth configure-docker "$AR_LOCATION-docker.pkg.dev" --quiet

# 4. Build & Push via Cloud Build
echo "🏗️  Building and pushing container via Cloud Build..."
if [ -f "$CLOUD_BUILD_CFG" ]; then
    gcloud builds submit --project="$PROJECT_ID" --config="$CLOUD_BUILD_CFG" \
        --substitutions="_REGION=$REGION,_REPO=$REPO_NAME,_DEPLOY_VERTEX=true"
else
    echo "⚠️  Cloud Build config not found at $CLOUD_BUILD_CFG, building locally..."
    
    # Build locally and push
    docker build -t "$IMAGE_URI" -f addons/sterling_os/Dockerfile .
    docker push "$IMAGE_URI"
fi

# 5. Create/Update Cloud Build Trigger
echo "🔄 Setting up Cloud Build trigger..."
if gcloud builds triggers list --project="$PROJECT_ID" --filter="name:$TRIGGER_NAME" --format="value(name)" | grep -q "$TRIGGER_NAME"; then
    echo "✅ Cloud Build trigger already exists: $TRIGGER_NAME"
else
    echo "🆕 Creating Cloud Build trigger..."
    gcloud builds triggers create github --project="$PROJECT_ID" \
        --name="$TRIGGER_NAME" \
        --repo-owner="$REPO_OWNER" \
        --repo-name="$REPO_NAME" \
        --branch-pattern="^main$" \
        --build-config="$CLOUD_BUILD_CFG" \
        --substitutions="_REGION=$REGION,_REPO=$REPO_NAME,_DEPLOY_VERTEX=true"
    echo "✅ Created Cloud Build trigger: $TRIGGER_NAME"
fi

# 6. Create or reuse Vertex AI Endpoint
echo "🤖 Setting up Vertex AI endpoint..."
ENDPOINT_ID=$(gcloud ai endpoints list --region="$REGION" --project="$PROJECT_ID" \
    --filter="displayName=\"$ENDPOINT_NAME\"" --format="value(name)" 2>/dev/null | head -1 || true)

if [ -z "$ENDPOINT_ID" ]; then
    echo "🆕 Creating new Vertex AI endpoint..."
    ENDPOINT_ID=$(gcloud ai endpoints create --region="$REGION" --project="$PROJECT_ID" \
        --display-name="$ENDPOINT_NAME" \
        --format="value(name)")
    echo "✅ Created Vertex AI endpoint: $ENDPOINT_ID"
else
    echo "✅ Using existing Vertex AI endpoint: $ENDPOINT_ID"
fi

# 7. Create BigQuery dataset for analytics
echo "📊 Setting up BigQuery dataset..."
DATASET_NAME="${BIGQUERY_DATASET:-sterling_ha_analytics}"
if ! bq show --project_id="$PROJECT_ID" "$DATASET_NAME" &>/dev/null; then
    bq mk --project_id="$PROJECT_ID" --location="$REGION" "$DATASET_NAME"
    echo "✅ Created BigQuery dataset: $DATASET_NAME"
else
    echo "✅ BigQuery dataset already exists: $DATASET_NAME"
fi

# 8. Setup monitoring and alerting
echo "📈 Setting up monitoring and alerting..."
if [ "${MONITORING_ENABLED:-true}" = "true" ]; then
    # Create a simple uptime check
    gcloud alpha monitoring uptime create \
        --project="$PROJECT_ID" \
        --display-name="Sterling HA Uptime Check" \
        --hostname="sterling-ha-endpoint" \
        --path="/health" \
        --port=8123 \
        --protocol=HTTP \
        --timeout=10s \
        --period=60s || echo "⚠️  Uptime check creation failed (may already exist)"
fi

# 9. Deploy Model Container to Endpoint (optional)
if [ "${DEPLOY_MODEL:-false}" = "true" ]; then
    echo "🚀 Deploying model to Vertex AI endpoint..."
    MODEL_NAME="sterling-ha-model-$(date +%Y%m%d%H%M%S)"
    
    # Create model
    gcloud ai models upload \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --display-name="$MODEL_NAME" \
        --container-image-uri="$IMAGE_URI" \
        --container-health-route="/health" \
        --container-predict-route="/predict" \
        --container-ports=8080 || echo "⚠️  Model upload failed"
    
    # Deploy to endpoint
    gcloud ai endpoints deploy-model "$ENDPOINT_ID" \
        --region="$REGION" \
        --project="$PROJECT_ID" \
        --model="$MODEL_NAME" \
        --display-name="$MODEL_NAME" \
        --traffic-split=0=100 \
        --machine-type="n1-standard-2" \
        --min-replica-count=1 \
        --max-replica-count=3 || echo "⚠️  Model deployment failed"
else
    echo "ℹ️  Skipping model deployment (set DEPLOY_MODEL=true to enable)"
fi

# 10. Update Home Assistant Add-on Config
echo "🏠 Updating Home Assistant add-on configuration..."
if [ -f "$HA_CONFIG" ]; then
    # Update config with new image URI
    if command -v jq &> /dev/null; then
        jq --arg img "$IMAGE_URI" '.image = $img' "$HA_CONFIG" > tmp.$$.json && mv tmp.$$.json "$HA_CONFIG"
        echo "✅ Updated HA add-on config with image: $IMAGE_URI"
    else
        echo "⚠️  jq not available, skipping config update"
    fi
else
    echo "⚠️  HA config not found at '$HA_CONFIG'"
fi

# 11. Create cost tracking script
echo "💰 Setting up cost tracking..."
cat > scripts/check_billing.sh << 'EOF'
#!/bin/bash
# BigQuery billing check script
set -euo pipefail

if [ -f ".env" ]; then
    # shellcheck disable=SC1091
    source .env
fi

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}"
THRESHOLD="${BILLING_ALERT_THRESHOLD:-100.00}"

# Query current month's costs
CURRENT_COST=$(bq query --use_legacy_sql=false --format=csv --max_rows=1 \
    "SELECT SUM(cost) as total_cost 
     FROM \`$PROJECT_ID.sterling_ha_analytics.billing_export\` 
     WHERE DATE(usage_start_time) >= DATE_TRUNC(CURRENT_DATE(), MONTH)" 2>/dev/null | tail -1 || echo "0")

echo "Current month cost: \$${CURRENT_COST}"
echo "Alert threshold: \$${THRESHOLD}"

if (( $(echo "$CURRENT_COST > $THRESHOLD" | bc -l) )); then
    echo "⚠️  BILLING ALERT: Cost exceeds threshold!"
    exit 1
else
    echo "✅ Billing within threshold"
fi
EOF

chmod +x scripts/check_billing.sh

echo "✅ Sterling HA Vertex AI deployment complete!"
echo ""
echo "📋 Summary:"
echo "  • Project: $PROJECT_ID"
echo "  • Region: $REGION"
echo "  • Artifact Registry: $AR_REPO"
echo "  • Container Image: $IMAGE_URI"
echo "  • Vertex AI Endpoint: $ENDPOINT_ID"
echo "  • BigQuery Dataset: $DATASET_NAME"
echo ""
echo "🔗 Useful commands:"
echo "  • View builds: gcloud builds list --project=$PROJECT_ID"
echo "  • View endpoints: gcloud ai endpoints list --region=$REGION --project=$PROJECT_ID"
echo "  • Check costs: ./scripts/check_billing.sh"
