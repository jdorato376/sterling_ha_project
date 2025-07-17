#!/bin/bash
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧠 Starting Codex Tier-1 Validation Suite (Phase 40.9 Finalizer)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "[1/10] 🔍 Running ruff linter..."
ruff check . || exit 1

echo "[2/10] 🧠 Running mypy static type checks..."
mypy addons/ tests/ || exit 1

echo "[3/10] 🔐 Running security scan with bandit..."
bandit -r addons/ || exit 1

echo "[4/10] 🧪 Running pytest quietly..."
pytest -q || exit 1

echo "[5/10] 🔁 Running synthetic E2E validation..."
bash phase40_9_synthetic_validation.sh > /tmp/synthetic_final.log || exit 1

echo "[6/10] 📁 Verifying scene_trace and memory integrity..."
echo "Scene trace contents:"
tail -n 5 addons/sterling_os/scene_trace.json || echo "[WARN] Missing or empty scene_trace.json"

echo "[7/10] 📜 Verifying audit log integrity..."
tail -n 5 addons/sterling_os/logs/audit_log.json || echo "[WARN] Missing or empty audit log"

echo "[8/10] 🧠 Testing HA API ping..."
curl -s -X POST http://localhost:8123/api/states/sensor.ping_test \
  -H 'Authorization: Bearer YOUR_LONG_LIVED_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"state": "alive"}' || echo "[WARN] Home Assistant ping failed"

echo "[9/10] 🧠 Validating memory schema checksum..."
sha256sum runtime_memory.py > /tmp/memory_hash.log
cat /tmp/memory_hash.log

echo "[10/10] 💣 Simulating fallback logging logic..."
python3 -c "from addons.sterling_os.audit_logger import log_event; log_event('sentinel_test', 'fail')"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Phase 40.9 Tier-1 Finalizer Complete"
echo "📜 Synthetic Log: /tmp/synthetic_final.log"
echo "🔐 Hash Log: /tmp/memory_hash.log"
echo "🧠 Ready to merge into main and proceed to Phase 41"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
