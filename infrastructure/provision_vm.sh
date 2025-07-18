#!/usr/bin/env bash
set -euo pipefail

# Sterling HA VM Provisioning Script
# Enhanced with HAOS, Shielded VM, private VPC, and Cloud NAT

# Load environment variables
if [ -f ".env" ]; then
    # shellcheck disable=SC1091
    source .env
fi

# Variables with defaults
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}"
REGION="${REGION:-us-central1}"
ZONE="${ZONE:-us-central1-a}"
VM_NAME="sterling-ha-vm"
MACHINE_TYPE="e2-medium"
BOOT_DISK_SIZE="50GB"
NETWORK_NAME="sterling-ha-vpc"
SUBNET_NAME="sterling-ha-subnet"
SERVICE_ACCOUNT="sterling-ha-sa@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🚀 Starting Sterling HA VM provisioning..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Zone: $ZONE"

# 1. Enable required APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable compute.googleapis.com \
    aiplatform.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    bigquery.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    --project="$PROJECT_ID"

# 2. Create VPC network if it doesn't exist
echo "🌐 Setting up VPC network..."
if ! gcloud compute networks describe "$NETWORK_NAME" --project="$PROJECT_ID" &>/dev/null; then
    gcloud compute networks create "$NETWORK_NAME" \
        --project="$PROJECT_ID" \
        --subnet-mode=custom \
        --description="Sterling HA private network"
fi

# 3. Create subnet if it doesn't exist
echo "🔗 Setting up subnet..."
if ! gcloud compute networks subnets describe "$SUBNET_NAME" --region="$REGION" --project="$PROJECT_ID" &>/dev/null; then
    gcloud compute networks subnets create "$SUBNET_NAME" \
        --project="$PROJECT_ID" \
        --network="$NETWORK_NAME" \
        --region="$REGION" \
        --range="10.0.1.0/24" \
        --enable-private-ip-google-access
fi

# 4. Create Cloud Router
echo "🔄 Setting up Cloud Router..."
if ! gcloud compute routers describe "sterling-ha-router" --region="$REGION" --project="$PROJECT_ID" &>/dev/null; then
    gcloud compute routers create "sterling-ha-router" \
        --project="$PROJECT_ID" \
        --network="$NETWORK_NAME" \
        --region="$REGION"
fi

# 5. Create Cloud NAT
echo "🌐 Setting up Cloud NAT..."
if ! gcloud compute routers nats describe "sterling-ha-nat" --router="sterling-ha-router" --region="$REGION" --project="$PROJECT_ID" &>/dev/null; then
    gcloud compute routers nats create "sterling-ha-nat" \
        --project="$PROJECT_ID" \
        --router="sterling-ha-router" \
        --region="$REGION" \
        --nat-all-subnet-ip-ranges
fi

# 6. Create firewall rules
echo "🔥 Setting up firewall rules..."
if ! gcloud compute firewall-rules describe "sterling-ha-firewall-internal" --project="$PROJECT_ID" &>/dev/null; then
    gcloud compute firewall-rules create "sterling-ha-firewall-internal" \
        --project="$PROJECT_ID" \
        --network="$NETWORK_NAME" \
        --allow=tcp:22,tcp:80,tcp:443,tcp:8123 \
        --source-ranges="10.0.1.0/24" \
        --target-tags="sterling-ha"
fi

if ! gcloud compute firewall-rules describe "sterling-ha-firewall-external" --project="$PROJECT_ID" &>/dev/null; then
    gcloud compute firewall-rules create "sterling-ha-firewall-external" \
        --project="$PROJECT_ID" \
        --network="$NETWORK_NAME" \
        --allow=tcp:22,tcp:80,tcp:443,tcp:8123 \
        --source-ranges="0.0.0.0/0" \
        --target-tags="sterling-ha,http-server,https-server"
fi

# 7. Create service account if it doesn't exist
echo "🔑 Setting up service account..."
if ! gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --project="$PROJECT_ID" &>/dev/null; then
    gcloud iam service-accounts create "sterling-ha-sa" \
        --project="$PROJECT_ID" \
        --display-name="Sterling HA Service Account" \
        --description="Service account for Sterling HA VM and services"
        
    # Add IAM roles
    for role in \
        "roles/compute.instanceAdmin.v1" \
        "roles/aiplatform.user" \
        "roles/artifactregistry.reader" \
        "roles/cloudbuild.builds.editor" \
        "roles/monitoring.metricWriter" \
        "roles/logging.logWriter" \
        "roles/bigquery.dataViewer"; do
        gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:$SERVICE_ACCOUNT" \
            --role="$role"
    done
fi

# 8. Import Home Assistant OS image (placeholder - would need actual HAOS QCOW2)
echo "💿 Checking for Home Assistant OS image..."
if ! gcloud compute images describe "haos-custom" --project="$PROJECT_ID" &>/dev/null; then
    echo "ℹ️  Using Ubuntu as base image (HAOS import would go here)"
    # In a real scenario, you would import the HAOS QCOW2 image here
    # gcloud compute images create haos-custom --source-uri=gs://bucket/haos.qcow2
fi

# 9. Create VM instance with Shielded VM
echo "🖥️  Creating VM instance with Shielded VM..."
if gcloud compute instances describe "$VM_NAME" --zone="$ZONE" --project="$PROJECT_ID" &>/dev/null; then
    echo "⚠️  VM $VM_NAME already exists, skipping creation"
else
    gcloud compute instances create "$VM_NAME" \
        --project="$PROJECT_ID" \
        --zone="$ZONE" \
        --machine-type="$MACHINE_TYPE" \
        --image-family="ubuntu-2204-lts" \
        --image-project="ubuntu-os-cloud" \
        --boot-disk-size="$BOOT_DISK_SIZE" \
        --boot-disk-type="pd-standard" \
        --network="$NETWORK_NAME" \
        --subnet="$SUBNET_NAME" \
        --no-address \
        --service-account="$SERVICE_ACCOUNT" \
        --scopes="cloud-platform" \
        --tags="sterling-ha,http-server,https-server" \
        --shielded-secure-boot \
        --shielded-vtpm \
        --shielded-integrity-monitoring \
        --metadata-from-file startup-script=<(cat <<'EOF'
#!/bin/bash
# VM startup script for Sterling HA

# Update system
apt-get update
apt-get install -y docker.io docker-compose python3 python3-pip git curl

# Enable Docker
systemctl enable docker
systemctl start docker

# Install Google Cloud Ops Agent
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
bash add-google-cloud-ops-agent-repo.sh --also-install

# Create Sterling HA directory
mkdir -p /opt/sterling-ha

# Pull Sterling HA container (if available)
PROJECT_ID=$(curl -s "http://metadata.google.internal/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google")
docker pull gcr.io/${PROJECT_ID}/sterling-ha-addon:latest || echo "Sterling HA image not yet available"

# Setup log rotation
cat > /etc/logrotate.d/sterling-ha << 'EOL'
/opt/sterling-ha/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOL

echo "✅ VM setup complete"
EOF
)
fi

# 10. Create Artifact Registry repository
echo "📦 Setting up Artifact Registry..."
if ! gcloud artifacts repositories describe "sterling-ha-repo" --location="$REGION" --project="$PROJECT_ID" &>/dev/null; then
    gcloud artifacts repositories create "sterling-ha-repo" \
        --project="$PROJECT_ID" \
        --repository-format=docker \
        --location="$REGION" \
        --description="Sterling HA Docker images"
fi

# 11. Create BigQuery dataset
echo "📊 Setting up BigQuery dataset..."
if ! bq show --project_id="$PROJECT_ID" sterling_ha_analytics &>/dev/null; then
    bq mk --project_id="$PROJECT_ID" --location="$REGION" sterling_ha_analytics
fi

echo "✅ Sterling HA VM provisioning complete!"
echo ""
echo "📋 Summary:"
echo "  • VM Name: $VM_NAME"
echo "  • Zone: $ZONE"
echo "  • Network: $NETWORK_NAME"
echo "  • Subnet: $SUBNET_NAME"
echo "  • Service Account: $SERVICE_ACCOUNT"
echo "  • Shielded VM: Enabled"
echo "  • Cloud NAT: Enabled"
echo ""
echo "🔗 Connect to VM:"
echo "  gcloud compute ssh $VM_NAME --zone=$ZONE --project=$PROJECT_ID"
