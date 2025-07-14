# Codex GPT Phase 4: Cognitive Execution Stack

Codex GPT Phase 4 introduces a lightweight cognitive execution layer that augments the existing Sterling OS agents. The goal is to provide time-aware routines, predictive behavior and structured memory without replacing current logic.

## Core Enhancements

### routine_engine.py – Context-Aware Execution Layer
This module evaluates simple context conditions and triggers Home Assistant scenes. Conditions can include time of day, calendar events and entity states. For example:

```python
from datetime import datetime
from addons.sterling_os import routine_engine

routine_engine.evaluate_routines(
    now=datetime.now(),
    states={"bedroom_lights": "on", "watch_active": True},
)
```

When run on a weekday morning with the bedroom lights on and the Apple Watch active, the `MorningOpsScene` is executed automatically.

### memory_timeline.py – Timeline Memory and Decision Logs
Structured timeline entries capture actions with timestamps so that large language models can recall prior decisions. Each entry follows this schema:

```json
{
  "timestamp": "2025-07-12T06:45:00",
  "action": "sterling.garage_check",
  "result": "closed",
  "initiator": "Sterling auto-check"
}
```

Functions `log_event()` and `load_timeline()` manage the JSON log for later analysis.
