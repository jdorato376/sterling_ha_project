# Codex Phase 11: Platinum Dominion Governor

This phase introduces a lightweight governor layer called **Platinum Dominion**. The governor oversees agent actions, records decisions and validates trust scores before high risk operations.

## Components
- `platinum/governor.py` – core class handling trust checks and logbook updates
- `platinum/diplomacy_matrix.json` – maps delegation and trust relationships
- `platinum/governance_logbook.yaml` – append-only record of escalations and approvals
- `platinum/trust_scores.json` – persistent trust ratings for agents
- `platinum/platinum_self_test.py` – verifies file integrity every 12 hours
- `.github/workflows/phase11-governor-check.yml` – CI task ensuring trust scores remain above the threshold

## Usage
Run `python platinum/governor.py --check --agent=codex --score-threshold=0.75` to assert the Codex agent meets the minimum trust rating. Any escalation via `escalation_engine.escalate_scene()` will also append to the governance logbook when the governor is available.
