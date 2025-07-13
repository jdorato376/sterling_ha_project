# Phase 11: Multi-Agent Constitution Layer

Sterling GPT enters the governance tier by defining a written constitution for all agents.

## Components
- **phase11_codex_constitution.json** – describes agent roles, allowed actions, and override rules.
- **agent_constitution.py** – helper functions to evaluate rules and escalation needs.
- **ha_gitops_sync.py** – clones Home Assistant config from GitHub and validates YAML.

## Usage
`can_act(agent, action)` returns ``True`` when an agent is permitted to perform `action`.
`requires_escalation(agent, action)` flags actions that must be approved by a human or higher authority.
`can_override(agent, target)` determines if one agent may override another.

This lightweight layer enforces boundaries before actions are executed and keeps the system auditable.
