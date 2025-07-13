# Codex Phase 8: Mission Resilience & Countermeasure Intelligence

This phase introduces a minimal resilience layer so scenes can fail gracefully and the system can recover automatically.

## Key Modules
- `resilience_engine.py` – logs agent failures and activates a failsafe state
- `audit_logger.py` – stores structured log events in `memory/audit_log.json`
- `scene_trace.py` – records every scene execution with status and quorum info

## Behavior
`log_failure(agent, context, desc)` appends a diagnostic entry and emits an audit log.
`activate_failsafe(reason)` writes `failsafe_state.json` with a snapshot of trust weights.
`reset_failsafe()` clears this file and logs the reset.

Use `resilience_status()` to check if the failsafe is active and how many failures are recorded.

These utilities extend Phase 7 without altering existing modules and include unit tests.
