# Codex Phase 9: Real-Time Self-Healing and Predictive Trust

This phase equips Sterling GPT with automatic recovery and rolling trust logic.

## Key Components
- `self_healing.py` – downgrades failing agents, reroutes intents and logs the event
- `predictive_trust.py` – maintains short-term success/failure history to compute trust
- `trust_registry.py` – persists updated scores
- `escalation_engine.py` – now provides `escalate_to_admin()` for notification

## Behavior
When an agent fails, `self_heal()` reduces its trust weight, finds an alternate
agent via the cognitive router and records the reroute in `scene_trace.json`.
Failures are escalated for review. `PredictiveTrustManager` calculates a trust
score based on successes vs. failures in the last hour.

These utilities extend Phase 8 resilience and include unit tests.
