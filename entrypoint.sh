#!/bin/bash
set -e

# Safe Git config inside Docker
git config --global --add safe.directory /app

# Remove stale index lock if it exists
if [ -f .git/index.lock ]; then
  rm -f .git/index.lock
fi

echo ">>> Pulling latest from Git..."
git pull origin main || echo ">>> Warning: git pull failed, continuing..."

echo ">>> Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Protect .env secrets
if [ -f .env ]; then
  chmod 600 .env
fi

# Log metadata for observability
log_metadata() {
  commit=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
  date=$(date -Iseconds)
  echo "{\"commit\": \"$commit\", \"timestamp\": \"$date\"}" > metadata.json
  echo ">>> Metadata logged: $commit at $date"
}

# Auto-push local changes if needed
auto_push() {
  if [ -n "$(git status --porcelain)" ]; then
    echo ">>> Uncommitted changes detected. Pushing..."
    git add -A
    git commit -m "[Sterling Auto-Fix]" || true

    if [ -n "$GIT_AUTH_TOKEN" ]; then
      repo_url=$(git config --get remote.origin.url)
      repo_url="${repo_url/https:\/\/github.com/https:\/\/$GIT_AUTH_TOKEN@github.com}"
      git push "$repo_url" HEAD:main || echo ">>> Warning: push failed"
    else
      git push origin HEAD:main || echo ">>> Warning: push failed"
    fi
  else
    echo ">>> Working directory clean. No push needed."
  fi
}

# Start Gunicorn with graceful trap
start_server() {
  echo ">>> Starting Sterling API..."
  gunicorn app:app -b 0.0.0.0:5000 --timeout 300 &
  child=$!
  trap 'echo ">>> Shutdown signal received"; kill $child; wait $child' TERM INT
  wait $child
}

log_metadata
auto_push

# Retry server on crash
until start_server; do
  echo ">>> Gunicorn crashed. Restarting in 5s..."
  auto_push
  sleep 5
done

