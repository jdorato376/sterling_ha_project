# Codex Phase 10: Autonomous Infrastructure Mastery

This phase adds predictive maintenance and rotation logic so Sterling GPT can keep itself stable.

## Key Modules
- `predictive_repair.py` – scans metrics and logs repair suggestions to `infra_resets.json`.
- `agent_rotation.py` – tracks success rates in `agent_scorecard.json` and reroutes failing agents.
- `api_watchdog.py` – disables unreliable APIs after repeated failures or high latency.
- `predictive_risk.py` – flags low trust weights or frequent anomalies and logs them via `codex_diagnostics.py`.

## Behavior
`predictive_repair()` returns a repair action when CPU, memory, load and network errors exceed safe levels.
`record_result()` in `agent_rotation` maintains a sliding window of outcomes; `should_rotate()` advises when to switch agents.
`api_watchdog.record_call()` marks endpoints disabled after three failures.
`evaluate_risk()` sends risk notices to `diagnostics_log.json`.

These modules extend Phase 9 with a lightweight infrastructure layer and include unit tests.
