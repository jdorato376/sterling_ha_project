# Codex GPT Phase 6: Escalation Intelligence & Behavior Auditing

Phase 6 introduces escalation logic, immutable behavior audits, and a diplomacy layer for resolving agent conflicts. Scene execution now persists status across reboots and every outcome is captured for review.

## Key Modules

- `escalation_engine.py` – escalates failed or disputed scenes and records the event.
- `behavior_audit.py` – writes JSONL audit entries with a SHA256 hash for verification.
- `diplomacy_protocol.py` – mediates agent disagreements and suggests trust rebalancing.
- `scene_status_tracker.py` – tracks scene state such as `awaiting_quorum`, `executed`, or `escalated`.
- `agent_senate.py` – now invokes escalation hooks when votes tie.

## Audit Log Structure

Entries in `audits/scene_audit.jsonl` contain a timestamp, action label, and related metadata. The companion `.sha256` file holds the running digest to confirm integrity.

## Manual Escalation

Call `escalation_engine.escalate_scene(scene_id, reason)` to force escalation. The scene state updates and a new audit line is written.

## Override Behavior

The executive can override any in-flight scene by invoking `scene_status_tracker.update_status(scene_id, "rejected")` before escalation completes. Audits will record the override so that trust adjustments accurately reflect executive input.

## Diplomacy Scoring

When agents disagree, `diplomacy_protocol.mediate()` compares weighted votes. A tie triggers escalation. The `propose_rebalance()` helper returns new trust scores based on the outcome.
