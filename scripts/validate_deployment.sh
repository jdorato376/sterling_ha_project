#!/bin/bash
PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE="ai-router"

check_service() {
  echo "🔍 Checking Cloud Run service..."
  gcloud run services describe $SERVICE --region $REGION --project $PROJECT_ID --format json > /dev/null
  if [ $? -eq 0 ]; then
    echo "✅ Service $SERVICE is live."
  else
    echo "❌ Service $SERVICE not found."
  fi
}

check_vertex() {
  echo "🔍 Checking Vertex API..."
  gcloud services list --enabled --project $PROJECT_ID | grep aiplatform > /dev/null
  if [ $? -eq 0 ]; then
    echo "✅ Vertex AI API is enabled."
  else
    echo "❌ Vertex AI API not enabled."
  fi
}

check_service
check_vertex
