import subprocess, os
from addons.sterling_os.audit_logger import log_event

def trigger_recovery():
    try:
        subprocess.call(["python3", "-m", "addons.sterling_os.ha_gitops_sync"])
        log_event("reflex_recovery", "success", {"method": "gitops_sync"})
        print("✅ Reflex Recovery Triggered")
    except Exception as e:
        log_event("reflex_recovery", "error", {"error": str(e)})
        print("❌ Reflex Recovery Failed")

if __name__ == "__main__":
    trigger_recovery()
