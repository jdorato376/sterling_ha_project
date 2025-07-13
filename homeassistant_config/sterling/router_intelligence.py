import random

from .audit_logger import log_event

AGENT_ROUTER = {
    "home_automation": ["Sterling", "HomeAssistant"],
    "financial": ["Sterling", "MonarchAI"],
    "health": ["Sterling", "AppleIntelligence"],
    "tasks": ["Sterling", "CodexGPT"],
    "fallback": ["Sterling", "GeminiAPI"],
}


def simulate_agent_call(agent: str) -> bool:
    return random.choice([True, False, True])


def route_task(task_category: str) -> dict:
    agents = AGENT_ROUTER.get(task_category, AGENT_ROUTER["fallback"])
    for agent in agents:
        try:
            log_event(f"📡 Routing '{task_category}' to {agent}")
            if simulate_agent_call(agent):
                return {"agent": agent, "status": "success"}
        except Exception as e:
            log_event(f"⚠️ {agent} failed: {str(e)}")
    return {"agent": "none", "status": "all failed"}
