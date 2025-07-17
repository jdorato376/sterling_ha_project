#!/usr/bin/env bash
# codex_mega_pipeline.sh — Orchestrate Codex to generate, commit, and push all automation scripts
# Leverages the OpenAI CLI to have Codex build out your 3-stage workflow in sterling_ha_project.

set -euo pipefail

# ────────────────────────────────────────────────────────────────────────────────
# PRE-FLIGHT CHECKS
# ────────────────────────────────────────────────────────────────────────────────

# 1) Ensure OpenAI CLI is installed and authenticated
if ! command -v openai &>/dev/null; then
  echo "❗️ Please install the OpenAI CLI: https://github.com/openai/openai-cli"
  exit 1
fi
: "${OPENAI_API_KEY:?Environment variable OPENAI_API_KEY must be set.}"

# 2) Ensure git is clean and on main
git fetch origin
git checkout main
if [ -n "$(git status --porcelain)" ]; then
  echo "❗️ Please commit or stash changes before running this script."
  exit 1
fi

# 3) Ensure scripts/ directory exists
mkdir -p scripts

# ────────────────────────────────────────────────────────────────────────────────
# 1) Generate Stage 0: setup_environment.sh
# ────────────────────────────────────────────────────────────────────────────────

echo "🔨 Generating scripts/setup_environment.sh via Codex..."
openai api chat.completions.create -m code-davinci-002 --temperature 0 \
  --system "You are Codex, an expert DevOps AI. Generate an idempotent bash script that:" \
  --user "Stage 0: Setup Environment
• Clone the repo: https://github.com/jdorato376/sterling_ha_project if missing
• Ensure CLIs: gcloud, docker, jq are installed
• Authenticate via GOOGLE_APPLICATION_CREDENTIALS
• Set GOOGLE_CLOUD_PROJECT and REGION (default us-central1)
• Validate presence of cloudbuild.yaml and Dockerfile
• Exit non-zero on any error
Output script to scripts/setup_environment.sh with executable permissions." \
  > scripts/setup_environment.sh

chmod +x scripts/setup_environment.sh

# ────────────────────────────────────────────────────────────────────────────────
# 2) Generate Stage 1: deploy_vertex.sh
# ────────────────────────────────────────────────────────────────────────────────

echo "🔨 Generating scripts/deploy_vertex.sh via Codex..."
openai api chat.completions.create -m code-davinci-002 --temperature 0 \
  --system "You are Codex, an expert DevOps AI. Generate an idempotent bash script that:" \
  --user "Stage 1: Deploy to Vertex AI
• Provision Artifact Registry 'sterling-ai-repo' in REGION
• Enable Cloud Build API
• Build & push container via cloudbuild.yaml
• Create or update a GitHub→Cloud Build trigger on main branch
• Create or reuse Vertex AI endpoint named 'Sterling HA Endpoint'
• Deploy the container image to that endpoint with 100% traffic on n1-standard-2
• Patch addons/sterling_os/config.json to point to the new image URI
• Commit all changes to origin/main
Output script to scripts/deploy_vertex.sh with executable permissions." \
  > scripts/deploy_vertex.sh

chmod +x scripts/deploy_vertex.sh

# ────────────────────────────────────────────────────────────────────────────────
# 3) Generate Stage 2: provision_ha.sh
# ────────────────────────────────────────────────────────────────────────────────

echo "🔨 Generating scripts/provision_ha.sh via Codex..."
openai api chat.completions.create -m code-davinci-002 --temperature 0 \
  --system "You are Codex, an expert in DevOps and Home Assistant. Generate an idempotent bash script that:" \
  --user "Stage 2: Provision Home Assistant Core
• Pull and run homeassistant/home-assistant:stable in Docker
• Mount local ./config to /config and ./addons to /addons
• Wait until HA API is available at http://localhost:8123
• Use HA_TOKEN to install and start the sterling_os add-on via Supervisor API
• Verify add-on health endpoint
Output script to scripts/provision_ha.sh with executable permissions." \
  > scripts/provision_ha.sh

chmod +x scripts/provision_ha.sh

# ────────────────────────────────────────────────────────────────────────────────
# 4) Update README.md “Getting Started”
# ────────────────────────────────────────────────────────────────────────────────

echo "✍️  Updating README.md with 3-stage workflow guidance..."
# Insert under “Getting Started” section or append if missing
if grep -q "## Getting Started" README.md; then
  awk '/## Getting Started/{print; print ""; print "```bash\n./scripts/setup_environment.sh && \\
./scripts/deploy_vertex.sh && \\
./scripts/provision_ha.sh\n```"; next}1' README.md > README.temp
  mv README.temp README.md
else
  cat <<'EOF2' >> README.md

## Getting Started

```bash
./scripts/setup_environment.sh && \
./scripts/deploy_vertex.sh && \
./scripts/provision_ha.sh
```
EOF2
fi

# ────────────────────────────────────────────────────────────────────────────────
# 5) Commit & Push
# ────────────────────────────────────────────────────────────────────────────────

echo "💾 Committing generated scripts to Git..."
git add scripts/setup_environment.sh scripts/deploy_vertex.sh scripts/provision_ha.sh README.md
git commit -m "chore: generate 3-stage bootstrap, Vertex deploy, and HA provisioning scripts via Codex"
git push origin main

echo "✅ All set! Codex has been busy building your 3-stage automation. Next: run the scripts to stand up HA & Vertex AI."
