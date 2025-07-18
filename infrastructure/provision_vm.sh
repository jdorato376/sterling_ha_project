#!/usr/bin/env bash
set -euo pipefail

# Sterling HA Project - VM Provisioning Script
# Phase 191: Provision a cost-friendly GCP VM with HA-Optimized OS
# Includes HAOS QCOW2 import, Shielded VM, private VPC, and Cloud NAT

# Load environment variables
if [ -f .env ]; then
    source .env
fi

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}"
REGION="${REGION:-us-central1}"
ZONE="${ZONE:-${REGION}-a}"
VM_NAME="sterling-ha-vm"
HAOS_IMAGE_URL="https://github.com/home-assistant/operating-system/releases/download/10.5/haos_generic-x86-64-10.5.img.xz"
HAOS_IMAGE_NAME="haos-generic-x86-64-10-5"

echo "🚀 Starting Sterling HA VM provisioning..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Zone: $ZONE"

# Enable required APIs
echo "📋 Enabling required GCP APIs..."
gcloud services enable compute.googleapis.com --project="$PROJECT_ID"
gcloud services enable artifactregistry.googleapis.com --project="$PROJECT_ID"
gcloud services enable cloudbuild.googleapis.com --project="$PROJECT_ID"

# Check if HAOS image exists, if not import it
echo "🔍 Checking for Home Assistant OS image..."
if ! gcloud compute images describe "$HAOS_IMAGE_NAME" --project="$PROJECT_ID" &>/dev/null; then
    echo "📥 Importing Home Assistant OS QCOW2 image..."
    
    # Create a temporary bucket for image upload
    TEMP_BUCKET="${PROJECT_ID}-haos-import"
    gsutil mb -p "$PROJECT_ID" "gs://$TEMP_BUCKET" || echo "Bucket already exists"
    
    # Download and upload HAOS image
    echo "⬇️  Downloading Home Assistant OS image..."
    curl -L "$HAOS_IMAGE_URL" -o haos.img.xz
    unxz haos.img.xz
    
    echo "⬆️  Uploading image to Cloud Storage..."
    gsutil cp haos.img "gs://$TEMP_BUCKET/haos.img"
    
    # Import the image
    echo "🔄 Importing image to Compute Engine..."
    gcloud compute images create "$HAOS_IMAGE_NAME" \
        --source-uri="gs://$TEMP_BUCKET/haos.img" \
        --family="home-assistant-os" \
        --project="$PROJECT_ID"
    
    # Clean up
    rm -f haos.img
    gsutil rm "gs://$TEMP_BUCKET/haos.img"
    gsutil rb "gs://$TEMP_BUCKET"
    
    echo "✅ Home Assistant OS image imported successfully"
else
    echo "✅ Home Assistant OS image already exists"
fi

# Create VPC network if it doesn't exist
VPC_NAME="sterling-ha-vpc"
if ! gcloud compute networks describe "$VPC_NAME" --project="$PROJECT_ID" &>/dev/null; then
    echo "🌐 Creating VPC network..."
    gcloud compute networks create "$VPC_NAME" \
        --subnet-mode=custom \
        --project="$PROJECT_ID"
fi

# Create subnet if it doesn't exist
SUBNET_NAME="sterling-ha-subnet"
if ! gcloud compute networks subnets describe "$SUBNET_NAME" --region="$REGION" --project="$PROJECT_ID" &>/dev/null; then
    echo "🔗 Creating subnet..."
    gcloud compute networks subnets create "$SUBNET_NAME" \
        --network="$VPC_NAME" \
        --range="10.0.1.0/24" \
        --region="$REGION" \
        --enable-private-ip-google-access \
        --project="$PROJECT_ID"
fi

# Create Cloud Router for NAT
ROUTER_NAME="sterling-ha-router"
if ! gcloud compute routers describe "$ROUTER_NAME" --region="$REGION" --project="$PROJECT_ID" &>/dev/null; then
    echo "🌐 Creating Cloud Router..."
    gcloud compute routers create "$ROUTER_NAME" \
        --network="$VPC_NAME" \
        --region="$REGION" \
        --project="$PROJECT_ID"
fi

# Create Cloud NAT
NAT_NAME="sterling-ha-nat"
if ! gcloud compute routers nats describe "$NAT_NAME" --router="$ROUTER_NAME" --region="$REGION" --project="$PROJECT_ID" &>/dev/null; then
    echo "🔄 Creating Cloud NAT..."
    gcloud compute routers nats create "$NAT_NAME" \
        --router="$ROUTER_NAME" \
        --auto-allocate-nat-external-ips \
        --nat-all-subnet-ip-ranges \
        --region="$REGION" \
        --project="$PROJECT_ID"
fi

# Create firewall rules
echo "🔥 Creating firewall rules..."
gcloud compute firewall-rules create sterling-ha-allow-http \
    --network="$VPC_NAME" \
    --allow=tcp:80,tcp:8123 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=sterling-ha-http \
    --project="$PROJECT_ID" \
    --quiet || echo "HTTP firewall rule already exists"

gcloud compute firewall-rules create sterling-ha-allow-https \
    --network="$VPC_NAME" \
    --allow=tcp:443 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=sterling-ha-https \
    --project="$PROJECT_ID" \
    --quiet || echo "HTTPS firewall rule already exists"

gcloud compute firewall-rules create sterling-ha-allow-ssh \
    --network="$VPC_NAME" \
    --allow=tcp:22 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=sterling-ha-ssh \
    --project="$PROJECT_ID" \
    --quiet || echo "SSH firewall rule already exists"

# Create service account if it doesn't exist
SA_NAME="sterling-ha-vm-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
if ! gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
    echo "🔐 Creating service account..."
    gcloud iam service-accounts create "$SA_NAME" \
        --display-name="Sterling HA VM Service Account" \
        --project="$PROJECT_ID"
    
    # Grant necessary permissions
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SA_EMAIL" \
        --role="roles/aiplatform.user"
    
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SA_EMAIL" \
        --role="roles/storage.admin"
fi

# Create the VM instance
echo "🖥️  Creating Sterling HA VM instance..."
gcloud compute instances create "$VM_NAME" \
    --project="$PROJECT_ID" \
    --zone="$ZONE" \
    --machine-type=e2-medium \
    --network-interface=network-tier=PREMIUM,subnet="$SUBNET_NAME",no-address \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --service-account="$SA_EMAIL" \
    --scopes=cloud-platform \
    --tags=sterling-ha-http,sterling-ha-https,sterling-ha-ssh \
    --image="$HAOS_IMAGE_NAME" \
    --boot-disk-size=32GB \
    --boot-disk-type=pd-standard \
    --boot-disk-device-name="$VM_NAME" \
    --shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --metadata=enable-oslogin=TRUE \
    --labels=project=sterling-ha,purpose=home-assistant \
    --quiet || echo "VM already exists or creation failed"

echo "✅ Sterling HA VM provisioning completed!"
echo "🔗 VM Name: $VM_NAME"
echo "🌐 Network: $VPC_NAME"
echo "📍 Zone: $ZONE"
echo "🔐 Service Account: $SA_EMAIL"
echo ""
echo "To connect to the VM:"
echo "gcloud compute ssh $VM_NAME --zone=$ZONE --project=$PROJECT_ID"
