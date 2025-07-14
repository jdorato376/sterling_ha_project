from __future__ import annotations

from collections import deque
from typing import Deque, Optional

from . import memory_manager
from . import scene_executor


class AutonomyEngine:
    """Minimal autonomous task manager."""

    def __init__(self) -> None:
        self.stack: Deque[str] = deque()
        self.current: Optional[str] = None

    def start_task(self, scene: str) -> None:
        """Push a new scene onto the end of the stack."""
        self.stack.append(scene)
        memory_manager.add_event(f"task_start:{scene}")

    def interrupt_task(self, scene: str) -> None:
        """Interrupt current task with a new high priority scene."""
        self.stack.appendleft(scene)
        memory_manager.add_event(f"task_interrupt:{scene}")

    async def run_next(self) -> Optional[str]:
        """Execute the next scene in the stack."""
        if not self.stack:
            return None
        self.current = self.stack.popleft()
        memory_manager.add_event(f"task_execute:{self.current}")
        await scene_executor.execute_scene(self.current)
        finished = self.current
        self.current = None
        return finished
