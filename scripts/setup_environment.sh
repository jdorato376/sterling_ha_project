#!/usr/bin/env bash
# Stage 0: prepare local environment
set -euo pipefail

# Clone repo if script not already inside it
if [ ! -d .git ]; then
  if [ ! -d sterling_ha_project/.git ]; then
    git clone https://github.com/jdorato376/sterling_ha_project.git sterling_ha_project
  fi
  cd sterling_ha_project
fi

# Ensure required CLIs
for cli in gcloud docker jq; do
  if ! command -v $cli &>/dev/null; then
    echo "❗️ $cli not found—install from https://cloud.google.com/sdk or https://www.docker.com"
    exit 1
  fi
done

# Authenticate
if [ -z "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]; then
  echo "❗️ GOOGLE_APPLICATION_CREDENTIALS is not set"
  exit 1
fi
gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"

# Configure project & region
: "${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT}"
: "${REGION:=us-central1}"
gcloud config set project "$GOOGLE_CLOUD_PROJECT"
gcloud config set compute/region "$REGION"

# Validate critical files
for file in cloudbuild.yaml Dockerfile; do
  if [ ! -f "$file" ]; then
    echo "❗️ Missing $file – verify path"
    exit 1
  fi
done

echo "✅ Stage 0: environment prep complete."
