from __future__ import annotations

"""Utility helpers for simple JSON file persistence."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict
import json
import os
import shutil
import logging

logger = logging.getLogger(__name__)


class JSONStoreError(Exception):
    """Raised when persisting data fails."""



@dataclass(slots=True)
class JSONStore:
    """Lightweight JSON file store wrapper."""

    path: Path
    default: Dict[str, Any] = field(default_factory=dict)

    def read(self) -> Dict[str, Any]:
        """Load JSON data from ``path`` or return ``default`` if invalid."""
        if not self.path.exists():
            return self.default.copy()
        try:
            with self.path.open() as f:
                content = f.read().strip()
                if not content:
                    return self.default.copy()
                return json.loads(content)
        except (json.JSONDecodeError, OSError, PermissionError):
            return self.default.copy()

    def write(self, data: Dict[str, Any]) -> None:
        """Write JSON data to ``path`` with indentation."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        try:
            with tmp_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            try:
                os.replace(tmp_path, self.path)
            except OSError:
                try:
                    shutil.move(tmp_path, self.path)
                except Exception as exc:
                    logger.exception("Atomic rename failed")
                    raise JSONStoreError(f"Failed to write {self.path}") from exc
        except (OSError, PermissionError) as exc:
            logger.exception("Write error")
            raise JSONStoreError(f"Failed to write {self.path}") from exc
        finally:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
