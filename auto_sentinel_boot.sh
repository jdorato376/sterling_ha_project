#!/usr/bin/env bash
# Quick bootstrap wrapper to immediately deploy Sterling in Sentinel Mode
# Requires HA_LONG_LIVED_TOKEN set in environment
set -euo pipefail

export HA_URL=${HA_URL:-"http://34.0.39.235:8123"}
export GITHUB_REPO=${GITHUB_REPO:-"https://github.com/jdorato376/sterling_ha_project.git"}
export GITHUB_BRANCH=${GITHUB_BRANCH:-"main"}

if [ -z "${HA_LONG_LIVED_TOKEN:-}" ]; then
  echo "ERROR: HA_LONG_LIVED_TOKEN is not set" >&2
  exit 1
fi

# Run the main deployment script from this repo
bash "$(dirname "$0")/sterling_sentinel_deploy.sh"

