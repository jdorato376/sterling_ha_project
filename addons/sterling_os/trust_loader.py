import yaml, json, os
from addons.sterling_os.audit_logger import log_event

TRUST_PATH = "config/trust_profile.yaml"
CACHE_PATH = "addons/sterling_os/logs/trust_cache.json"

def load_trust_profile():
    try:
        with open(TRUST_PATH, 'r') as f:
            profile = yaml.safe_load(f)
        with open(CACHE_PATH, 'w') as out:
            json.dump(profile, out, indent=2)
        log_event("load_trust_profile", "success", {"loaded": True})
        print("✅ Trust profile loaded.")
    except Exception as e:
        log_event("load_trust_profile", "error", {"error": str(e)})
        print(f"❌ Failed to load trust profile: {e}")

if __name__ == "__main__":
    load_trust_profile()
