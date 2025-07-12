#!/bin/bash
set -e

# Ensure git is usable in container
git config --global --add safe.directory /app
if [ -f .git/index.lock ]; then
  rm -f .git/index.lock
fi

echo ">>> Pulling latest from Git..."
git pull origin main || true

echo ">>> Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

if [ -f .env ]; then
  chmod 600 .env
fi

log_metadata() {
  commit=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
  date=$(date -Iseconds)
  echo "{\"commit\": \"$commit\", \"timestamp\": \"$date\"}" > metadata.json
}

auto_push() {
  git_status=$(git status --porcelain)
  if [ -n "$git_status" ]; then
    git add -A
    git commit -m "[Sterling Auto-Fix]" || true
    if [ -n "$GIT_AUTH_TOKEN" ]; then
      repo_url=$(git config --get remote.origin.url)
      repo_url="${repo_url/https:\/\/github.com/https:\/\/$GIT_AUTH_TOKEN@github.com}"
      git push "$repo_url" HEAD:main || true
    else
      git push origin HEAD:main || true
    fi
  fi
}

log_metadata
auto_push

start_server() {
  gunicorn app:app -b 0.0.0.0:5000 --timeout 300 &
  child=$!
  trap 'echo ">>> Caught termination signal"; kill $child; wait $child' TERM INT
  wait $child
}

until start_server; do
  echo ">>> Gunicorn crashed. Restarting in 5s..."
  auto_push
  sleep 5
done

