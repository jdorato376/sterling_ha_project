# Phase 7: Predictive Recovery + Trust-Aware Routing

This phase introduces two small modules that extend the previous Codex stack.

## Components
- **predictive_recovery.py** – writes scene checkpoints to `/config/.codex_recovery.json` so the system can restore after crashes.
- **smart_router.py** – selects the highest trusted agent above `TRUST_THRESHOLD` and falls back to `fallback_router` if none succeed.
- **trust_registry.py** – holds evolving trust scores used by the router.

## Usage
`save_checkpoint(scene_id, data)` records the latest scene state. Retrieve it later with `get_last_checkpoint(scene_id)`.

`smart_route(intent, context)` consults the trust registry and returns the chosen agent response. If all agents fail or fall below the threshold, the router returns `fallback_to_safe_mode(intent)`.

These utilities are fully backward compatible with earlier phases and covered by simple unit tests.
