import json
import datetime


def inject_event_prediction(agent_id: str, query: str, timestamp: str) -> None:
    """Update reflex intelligence files with prediction data."""
    horizon_path = "addons/sterling_os/reflex_intelligence/event_horizon.json"
    index_path = "addons/sterling_os/reflex_intelligence/reflex_index.json"

    try:
        with open(horizon_path, "r") as f:
            horizon = json.load(f)
        with open(index_path, "r") as f:
            index = json.load(f)

        today = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        if "remind" in query.lower() or "due" in query.lower():
            index.setdefault("proactive_suggestions", []).append(
                {
                    "agent": agent_id,
                    "suggestion": "Set reminder or calendar anchor",
                    "timestamp": today,
                }
            )

        horizon["last_sync"] = today

        with open(horizon_path, "w") as f:
            json.dump(horizon, f, indent=2)
        with open(index_path, "w") as f:
            json.dump(index, f, indent=2)
    except Exception as e:
        print(f"[Reflex Engine Error] {e}")
