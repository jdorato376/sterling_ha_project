import json


def enforce_governance(agent_id: str, action: str, requires_approval: bool = True) -> dict:
    """Enforce Platinum Dominion constitutional rules."""
    with open("addons/sterling_os/platinum_dominion/constitution.json", "r") as f:
        charter = json.load(f)

    if charter["core_principles"].get("human_governance") and requires_approval:
        if agent_id not in charter["executive_layer"]["executive_agents"]:
            return {
                "status": "halted",
                "reason": "Human approval required under constitutional law.",
                "agent": agent_id,
            }

    return {"status": "approved"}
