#!/bin/bash
if ! grep -q 'success' addons/sterling_os/logs/audit_log.json; then
  echo "[FAILURE] Reverting..."
  git reset --hard HEAD~1 && ./entrypoint.sh
fi
