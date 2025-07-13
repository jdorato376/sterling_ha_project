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

    # Check HA API
    curl_status = run_command("curl -s http://homeassistant.local:8123/api/ | grep -q message")
    result["ha_api"] = "reachable" if curl_status.returncode == 0 else "unreachable"

    # YAML check
    yaml_test = run_command("docker run -v /config:/config --rm ghcr.io/home-assistant/home-assistant:stable --script check_config")
    result["yaml_valid"] = yaml_test.returncode == 0

    # Canary toggle test
    toggle = run_command(
        "curl -s -X POST -H \"Authorization: Bearer $HA_LONG_LIVED_TOKEN\" -H \"Content-Type: application/json\" -d '{\"entity_id\":\"input_boolean.canary_test\"}' http://homeassistant.local:8123/api/services/input_boolean/toggle"
    )
    result["canary_test"] = "toggled" if toggle.returncode == 0 else "failed"

    # Git snapshot
    git_rev = run_command("git rev-parse --short HEAD")
    result["git_commit"] = git_rev.stdout.decode().strip()

    # Rollback if broken
    if not result["yaml_valid"]:
        run_command("git reset --hard HEAD~1")
        result["rollback_triggered"] = True

    # Save report
    with open("/config/sterling_exec/reflex/reflex_report.json", "w") as f:
        json.dump(result, f, indent=2)

    return result


if __name__ == "__main__":
    output = reflex_diagnostic()
    print(json.dumps(output, indent=2))
