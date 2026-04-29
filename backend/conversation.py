"""
CampusRule AI v2.0 — Conversation Memory module.

SQLite-backed multi-turn conversation storage with context awareness.
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(__file__).parent / os.getenv("DB_PATH", "data/campusrule.db")


def _get_db() -> sqlite3.Connection:
    """Get a database connection, creating tables if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            user_id TEXT DEFAULT NULL,
            pinned INTEGER DEFAULT 0,
            metadata TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            sources TEXT DEFAULT '[]',
            confidence REAL DEFAULT 0.0,
            follow_ups TEXT DEFAULT '[]',
            intent TEXT DEFAULT 'general',
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        );

        CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);
        CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at);
    """)
    return conn


def create_conversation(conversation_id: str = None, user_id: str = None) -> str:
    """Create a new conversation."""
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    conn = _get_db()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO conversations (id, created_at, updated_at, user_id) VALUES (?, ?, ?, ?)",
            (conversation_id, now, now, user_id),
        )
        conn.commit()
    finally:
        conn.close()

    return conversation_id


def add_message(
    conversation_id: str,
    role: str,
    content: str,
    sources: List[Dict] = None,
    confidence: float = 0.0,
    follow_ups: List[str] = None,
    intent: str = "general",
) -> str:
    """Add a message to a conversation."""
    message_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    conn = _get_db()
    try:
        # Ensure conversation exists
        conn.execute(
            "INSERT OR IGNORE INTO conversations (id, created_at, updated_at) VALUES (?, ?, ?)",
            (conversation_id, now, now),
        )

        # Insert message
        conn.execute(
            """INSERT INTO messages (id, conversation_id, role, content, timestamp, sources, confidence, follow_ups, intent)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                message_id,
                conversation_id,
                role,
                content,
                now,
                json.dumps(sources or []),
                confidence,
                json.dumps(follow_ups or []),
                intent,
            ),
        )

        # Update conversation title from first user message
        first_user = conn.execute(
            "SELECT content FROM messages WHERE conversation_id = ? AND role = 'user' ORDER BY timestamp LIMIT 1",
            (conversation_id,),
        ).fetchone()
        if first_user:
            title = first_user["content"][:80]
            conn.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
                (title, now, conversation_id),
            )

        conn.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (now, conversation_id),
        )

        conn.commit()
    finally:
        conn.close()

    return message_id


def get_conversation(conversation_id: str) -> Optional[Dict]:
    """Get full conversation with messages."""
    conn = _get_db()
    try:
        conv = conn.execute(
            "SELECT * FROM conversations WHERE id = ?",
            (conversation_id,),
        ).fetchone()

        if not conv:
            return None

        messages = conn.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp",
            (conversation_id,),
        ).fetchall()

        return {
            "conversation_id": conv["id"],
            "title": conv["title"],
            "created_at": conv["created_at"],
            "updated_at": conv["updated_at"],
            "pinned": bool(conv["pinned"]),
            "messages": [
                {
                    "id": msg["id"],
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg["timestamp"],
                    "sources": json.loads(msg["sources"]),
                    "confidence": msg["confidence"],
                    "follow_ups": json.loads(msg["follow_ups"]),
                    "intent": msg["intent"],
                }
                for msg in messages
            ],
        }
    finally:
        conn.close()


def get_conversation_history(conversation_id: str, limit: int = 10) -> List[Dict]:
    """Get recent messages for context building."""
    conn = _get_db()
    try:
        messages = conn.execute(
            "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY timestamp DESC LIMIT ?",
            (conversation_id, limit),
        ).fetchall()

        return [{"role": msg["role"], "content": msg["content"]} for msg in reversed(messages)]
    finally:
        conn.close()


def list_conversations(user_id: str = None, limit: int = 20) -> List[Dict]:
    """List recent conversations."""
    conn = _get_db()
    try:
        if user_id:
            rows = conn.execute(
                """SELECT c.*, COUNT(m.id) as message_count
                   FROM conversations c
                   LEFT JOIN messages m ON c.id = m.conversation_id
                   WHERE c.user_id = ?
                   GROUP BY c.id
                   ORDER BY c.pinned DESC, c.updated_at DESC
                   LIMIT ?""",
                (user_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT c.*, COUNT(m.id) as message_count
                   FROM conversations c
                   LEFT JOIN messages m ON c.id = m.conversation_id
                   GROUP BY c.id
                   ORDER BY c.pinned DESC, c.updated_at DESC
                   LIMIT ?""",
                (limit,),
            ).fetchall()

        return [
            {
                "conversation_id": r["id"],
                "title": r["title"],
                "created_at": r["created_at"],
                "updated_at": r["updated_at"],
                "pinned": bool(r["pinned"]),
                "message_count": r["message_count"],
            }
            for r in rows
        ]
    finally:
        conn.close()


def pin_conversation(conversation_id: str, pinned: bool = True):
    """Pin or unpin a conversation."""
    conn = _get_db()
    try:
        conn.execute(
            "UPDATE conversations SET pinned = ? WHERE id = ?",
            (1 if pinned else 0, conversation_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_conversation(conversation_id: str):
    """Delete a conversation and its messages."""
    conn = _get_db()
    try:
        conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        conn.commit()
    finally:
        conn.close()


def cleanup_old_conversations(hours: int = 48):
    """Remove conversations older than the specified hours."""
    cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    conn = _get_db()
    try:
        conn.execute(
            "DELETE FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE updated_at < ? AND pinned = 0)",
            (cutoff,),
        )
        conn.execute(
            "DELETE FROM conversations WHERE updated_at < ? AND pinned = 0",
            (cutoff,),
        )
        conn.commit()
    finally:
        conn.close()
