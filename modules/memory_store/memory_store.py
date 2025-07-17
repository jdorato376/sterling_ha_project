"""
Phase 4: Persistent Memory Store
Implements SQLite and Firestore backends for agent memory.
"""
import sqlite3

class MemoryStore:
    def __init__(self, db_path="memory.db"):
        self.conn = sqlite3.connect(db_path)
        # TODO: migrate schema

    def write(self, key: str, value: str):
        # TODO: upsert memory entry
        pass

    def read(self, key: str) -> str:
        # TODO: fetch memory entry
        return ""
