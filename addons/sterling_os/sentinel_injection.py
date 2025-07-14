"""Sentinel mode injection script used during automated tests."""

from addons.sterling_os.audit_logger import log_event

# `log_event` only accepts a level and message. Encode the additional metadata
# as a formatted string to avoid TypeError during pytest collection.
payload = "trigger=manual phase=21"
log_event("sentinel_test_injection", f"failure {payload}")
print("🔍 Sentinel test scenario injected.")
