from addons.sterling_os.audit_logger import log_event
log_event("sentinel_test_injection", "failure", {"trigger": "manual", "phase": "21"})
print("🔍 Sentinel test scenario injected.")
