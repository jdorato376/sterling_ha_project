#!/bin/bash
echo "[Sterling GPT] Creating .env from Google Cloud secrets..."

ENV_FILE=".env"
> $ENV_FILE

SECRETS=(
  "OPENAI_API_KEY"
  "TWILIO_AUTH_TOKEN"
  "TWILIO_ACCOUNT_SID"
  "TWILIO_PHONE_NUMBER"
  "MONARCH_EMAIL"
  "MONARCH_PASSWORD"
  "GEMINI_API_KEY"
  "GOOGLE_AI_API_KEY"
  "GOOGLE_OAUTH_CLIENT_ID"
  "GOOGLE_OAUTH_CLIENT_SECRET"
  "DATABASE_URL"
  "FLASK_API"
  "SESSION_SECRET"
  "NODE_RED_ADMIN_HASH"
  "PGDATABASE"
  "PGHOST"
  "PGPASSWORD"
  "PGPORT"
  "PGUSER"
  "OPENROUTER_API_KEY"
)

for secret in "${SECRETS[@]}"; do
  VALUE=$(gcloud secrets versions access latest --secret="$secret" 2>/dev/null)
  if [ -z "$VALUE" ]; then
    echo "[WARNING] Secret not found or empty!"
  else
    echo "$secret=$VALUE" >> $ENV_FILE
  fi
done

chmod 600 "$ENV_FILE"
echo "[Sterling GPT] All secrets are locked and loaded in .env!"

