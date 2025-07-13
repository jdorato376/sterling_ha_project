#!/bin/bash
echo "🧠 Running Sterling Reflex Engine..."
python3 /config/sterling_exec/reflex/reflex_engine.py

# === Phase 4: Timeline Hook Trigger ===
echo "📜 Updating Sterling Timeline"
python3 /config/sterling_exec/timeline/timeline_engine.py
