#!/usr/bin/env bash
# Sterling GPT Phase 3: Reflex & Rollback Intelligence
# Auto-diagnose, validate, and heal the Sterling GPT + Home Assistant stack
set -euo pipefail

echo "\xF0\x9F\x9A\x80 PHASE 3: Reflex Engine Deploy Begin"
cd /config || { echo "\xE2\x9D\x8C /config not found"; exit 1; }

# Setup directories
mkdir -p /config/sterling_exec/reflex
mkdir -p /config/sterling_exec/hooks

cat <<'PY' > /config/sterling_exec/reflex/reflex_engine.py
import os
import subprocess
import json
import datetime


def run_command(cmd):
    return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def reflex_diagnostic():
    result = {
        "timestamp": datetime.datetime.now().isoformat(),
        "ha_api": "unknown",
        "yaml_valid": False,
        "canary_test": "missing",
        "rollback_triggered": False,
        "git_commit": "",
    }

    curl_status = run_command("curl -s http://homeassistant.local:8123/api/ | grep -q message")
    result["ha_api"] = "reachable" if curl_status.returncode == 0 else "unreachable"

    yaml_test = run_command("docker run -v /config:/config --rm ghcr.io/home-assistant/home-assistant:stable --script check_config")
    result["yaml_valid"] = yaml_test.returncode == 0

    toggle = run_command(
        "curl -s -X POST -H \"Authorization: Bearer $HA_LONG_LIVED_TOKEN\" -H \"Content-Type: application/json\" -d '{\"entity_id\":\"input_boolean.canary_test\"}' http://homeassistant.local:8123/api/services/input_boolean/toggle"
    )
    result["canary_test"] = "toggled" if toggle.returncode == 0 else "failed"

    git_rev = run_command("git rev-parse --short HEAD")
    result["git_commit"] = git_rev.stdout.decode().strip()

    if not result["yaml_valid"]:
        run_command("git reset --hard HEAD~1")
        result["rollback_triggered"] = True

    with open("/config/sterling_exec/reflex/reflex_report.json", "w") as f:
        json.dump(result, f, indent=2)

    return result


if __name__ == "__main__":
    output = reflex_diagnostic()
    print(json.dumps(output, indent=2))
PY

chmod 644 /config/sterling_exec/reflex/reflex_engine.py

echo "\xE2\x9C\x85 Reflex Engine Written"

cat <<'SH' > /config/sterling_exec/hooks/git_post_pull.sh
#!/bin/bash
echo "\xF0\x9F\xA7\xA0 Running Sterling Reflex Engine..."
python3 /config/sterling_exec/reflex/reflex_engine.py
SH

chmod +x /config/sterling_exec/hooks/git_post_pull.sh

echo "\xF0\x9F\x94\x92 Optional: schedule reflex_engine.py on boot or post-pull"
echo "\xF0\x9F\x93\x9C Sample manual test: python3 /config/sterling_exec/reflex/reflex_engine.py"

echo "\xE2\x9C\x85 Reflex & Rollback Resilience Layer Enabled"
