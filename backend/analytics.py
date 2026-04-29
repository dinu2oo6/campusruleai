"""
CampusRule AI v2.0 — Analytics module.

SQLite-backed tracking for questions, response times, confidence, topics,
trending detection, and satisfaction metrics.
"""

import json
import os
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(__file__).parent / os.getenv("DB_PATH", "data/campusrule.db")


def _get_db() -> sqlite3.Connection:
    """Get database connection with analytics tables."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS analytics_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            query TEXT DEFAULT '',
            category TEXT DEFAULT 'general',
            confidence REAL DEFAULT 0.0,
            response_time REAL DEFAULT 0.0,
            intent TEXT DEFAULT 'general',
            timestamp TEXT NOT NULL,
            metadata TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT NOT NULL,
            conversation_id TEXT NOT NULL,
            rating INTEGER DEFAULT 0,
            helpful INTEGER DEFAULT 1,
            comment TEXT DEFAULT '',
            timestamp TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics_events(timestamp);
        CREATE INDEX IF NOT EXISTS idx_analytics_type ON analytics_events(event_type);
        CREATE INDEX IF NOT EXISTS idx_feedback_message ON feedback(message_id);
    """)
    return conn


# ── Event Tracking ───────────────────────────────────────────────────────────

def track_query(
    query: str,
    category: str = "general",
    confidence: float = 0.0,
    response_time: float = 0.0,
    intent: str = "general",
    metadata: Dict = None,
):
    """Track a user query event."""
    conn = _get_db()
    try:
        conn.execute(
            """INSERT INTO analytics_events (event_type, query, category, confidence, response_time, intent, timestamp, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "query",
                query,
                category,
                confidence,
                response_time,
                intent,
                datetime.utcnow().isoformat(),
                json.dumps(metadata or {}),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def save_feedback(
    message_id: str,
    conversation_id: str,
    rating: int,
    helpful: bool = True,
    comment: str = "",
):
    """Save user feedback on a response."""
    conn = _get_db()
    try:
        conn.execute(
            """INSERT INTO feedback (message_id, conversation_id, rating, helpful, comment, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (message_id, conversation_id, rating, 1 if helpful else 0, comment, datetime.utcnow().isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


# ── Analytics Queries ────────────────────────────────────────────────────────

def get_analytics(days: int = 30) -> Dict:
    """Get comprehensive analytics for the dashboard."""
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

    conn = _get_db()
    try:
        # Total questions
        total = conn.execute(
            "SELECT COUNT(*) as cnt FROM analytics_events WHERE event_type = 'query' AND timestamp > ?",
            (cutoff,),
        ).fetchone()["cnt"]

        # Average response time
        avg_time = conn.execute(
            "SELECT AVG(response_time) as avg_t FROM analytics_events WHERE event_type = 'query' AND timestamp > ?",
            (cutoff,),
        ).fetchone()["avg_t"] or 0.0

        # Average confidence
        avg_conf = conn.execute(
            "SELECT AVG(confidence) as avg_c FROM analytics_events WHERE event_type = 'query' AND timestamp > ?",
            (cutoff,),
        ).fetchone()["avg_c"] or 0.0

        # Questions by category
        cat_rows = conn.execute(
            """SELECT category, COUNT(*) as cnt
               FROM analytics_events
               WHERE event_type = 'query' AND timestamp > ?
               GROUP BY category
               ORDER BY cnt DESC""",
            (cutoff,),
        ).fetchall()
        questions_by_category = {r["category"]: r["cnt"] for r in cat_rows}

        # Top policies (most queried topics)
        top_rows = conn.execute(
            """SELECT query, COUNT(*) as cnt, AVG(confidence) as avg_conf
               FROM analytics_events
               WHERE event_type = 'query' AND timestamp > ?
               GROUP BY query
               ORDER BY cnt DESC
               LIMIT 10""",
            (cutoff,),
        ).fetchall()
        top_policies = [
            {"query": r["query"], "count": r["cnt"], "avg_confidence": round(r["avg_conf"], 2)}
            for r in top_rows
        ]

        # Trending questions (last 7 days vs previous 7)
        week_cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()
        prev_week_cutoff = (datetime.utcnow() - timedelta(days=14)).isoformat()

        recent = conn.execute(
            """SELECT query, COUNT(*) as cnt
               FROM analytics_events
               WHERE event_type = 'query' AND timestamp > ?
               GROUP BY query
               ORDER BY cnt DESC
               LIMIT 10""",
            (week_cutoff,),
        ).fetchall()

        trending = []
        for r in recent:
            prev_count = conn.execute(
                """SELECT COUNT(*) as cnt FROM analytics_events
                   WHERE event_type = 'query' AND query = ? AND timestamp > ? AND timestamp <= ?""",
                (r["query"], prev_week_cutoff, week_cutoff),
            ).fetchone()["cnt"]

            growth = r["cnt"] - prev_count
            trending.append({
                "query": r["query"],
                "count": r["cnt"],
                "growth": growth,
                "trending": growth > 0,
            })

        # Questions over time (daily)
        daily = conn.execute(
            """SELECT DATE(timestamp) as day, COUNT(*) as cnt
               FROM analytics_events
               WHERE event_type = 'query' AND timestamp > ?
               GROUP BY DATE(timestamp)
               ORDER BY day""",
            (cutoff,),
        ).fetchall()
        questions_over_time = [{"date": r["day"], "count": r["cnt"]} for r in daily]

        # Peak hours
        hours = conn.execute(
            """SELECT CAST(strftime('%H', timestamp) AS INTEGER) as hour, COUNT(*) as cnt
               FROM analytics_events
               WHERE event_type = 'query' AND timestamp > ?
               GROUP BY hour
               ORDER BY hour""",
            (cutoff,),
        ).fetchall()
        peak_hours = [{"hour": r["hour"], "count": r["cnt"]} for r in hours]

        # Satisfaction rating
        avg_rating = conn.execute(
            "SELECT AVG(rating) as avg_r FROM feedback WHERE timestamp > ?",
            (cutoff,),
        ).fetchone()["avg_r"] or 0.0

        return {
            "total_questions": total,
            "avg_response_time": round(avg_time, 2),
            "avg_confidence": round(avg_conf, 1),
            "top_policies": top_policies,
            "trending_questions": trending,
            "questions_by_category": questions_by_category,
            "questions_over_time": questions_over_time,
            "peak_hours": peak_hours,
            "satisfaction_rating": round(avg_rating, 1),
        }
    finally:
        conn.close()
