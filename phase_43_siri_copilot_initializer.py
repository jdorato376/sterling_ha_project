# -*- coding: utf-8 -*-
"""Phase 43: Siri-Copilot Unified Orchestration Layer."""
from sterling_core.executive_router import ExecutiveRouter
from sterling_core.scene_orchestrator import SceneOrchestrator
from addons.sterling_os.trust.trust_registry import TrustRegistry
from addons.sterling_os.agents import (
    GPTProfessionalAssistant,
    GPTPersonalAssistant,
    SiriInterface,
    CopilotHR,
    CopilotIT,
    CopilotFinance,
    CopilotClinical,
    CopilotExecutiveAssistant,
)
from addons.sterling_os.voice.voice_dispatcher import SiriCopilotVoiceOrchestrator
from addons.sterling_os.daily_briefing.dispatch_summary import generate_executive_summary


def main() -> None:
    """Initialize unified voice orchestration."""
    # 🔒 Establish trust boundary
    trust_registry = TrustRegistry.load(
        "addons/sterling_os/trust/trust_registry.json"
    )

    # 🧠 Load Assistants
    exec_assistant = GPTProfessionalAssistant(trust_registry=trust_registry)
    personal_assistant = GPTPersonalAssistant()
    siri_interface = SiriInterface()
    voice_orchestrator = SiriCopilotVoiceOrchestrator(
        siri_interface=siri_interface,
        assistants={
            "professional": exec_assistant,
            "personal": personal_assistant,
        },
        copilots={
            "HR": CopilotHR(),
            "IT": CopilotIT(),
            "Finance": CopilotFinance(),
            "Clinical": CopilotClinical(),
            "Executive": CopilotExecutiveAssistant(),
        },
    )

    # 📆 Trigger Daily Executive Summary
    exec_summary = generate_executive_summary(
        sources=[
            "healthcare_news",
            "finance_updates",
            "ai_law_changes",
            "homecare_regulations",
        ],
        assistants=[exec_assistant, personal_assistant],
    )

    # 🗣️ Launch Unified Voice Router
    router = ExecutiveRouter()
    scene_orchestrator = SceneOrchestrator(router=router)

    scene_orchestrator.bind_voice_dispatcher(voice_orchestrator)
    scene_orchestrator.route_summary(exec_summary)

    # 📣 Log Success
    print("\u2501" * 48)
    print("\u2705 Sterling OS Phase 43 Initialized")
    print("\ud83d\udd17 Unified Siri + Copilot Executive Orchestration Online")
    print("\ud83d\udce8 Daily Executive Summary Ready for Dispatch")
    print("\ud83d\udd01 Persona Routing: Professional \u2194 Personal Contexts Enabled")
    print("\u2501" * 48)


if __name__ == "__main__":
    main()
