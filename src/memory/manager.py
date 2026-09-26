import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from src.core.config import settings

class TieredMemoryManager:
    """
    Tiered Memory Architecture:
    - L1: Working context (conversation buffer)
    - L2: Hierarchical Rules (AGENTS.md / directory policies)
    - L3: Ephemeral scratchpad
    - L4: Persistent Long-Term Memory (SQLite / Mem0)
    """
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (settings.project_root / ".memory.db")
        self._init_sqlite()

    def _init_sqlite(self) -> None:
        """Initializes local persistent memory database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def get_l2_rules(self) -> str:
        """Loads repository-wide constraints and guidelines from AGENTS.md."""
        if settings.rules_file.exists():
            try:
                return settings.rules_file.read_text(encoding="utf-8")
            except Exception:
                return ""
        return ""

    def add_l4_memory(self, content: str, category: str = "general", metadata: Optional[Dict[str, Any]] = None) -> int:
        """Stores a persistent insight or user preference in L4 memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
            INSERT INTO long_term_memory (category, content, metadata, created_at)
            VALUES (?, ?, ?, ?)
        """, (category, content, json.dumps(metadata or {}), now))
        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return memory_id or 0

    def query_l4_memory(self, query: str = "", limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves persistent memories relevant to query."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if query:
            cursor.execute("""
                SELECT id, category, content, metadata, created_at
                FROM long_term_memory
                WHERE content LIKE ?
                ORDER BY id DESC LIMIT ?
            """, (f"%{query}%", limit))
        else:
            cursor.execute("""
                SELECT id, category, content, metadata, created_at
                FROM long_term_memory
                ORDER BY id DESC LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "category": r[1],
                "content": r[2],
                "metadata": json.loads(r[3] or "{}"),
                "created_at": r[4]
            })
        return results

memory_manager = TieredMemoryManager()
