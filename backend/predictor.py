"""
CampusRule AI v2.0 — Autocomplete / Next-Word Prediction Engine.

Trie-based autocomplete with multi-layer suggestion ranking:
  Layer 1: Frequency-based (most asked questions)
  Layer 2: Semantic similarity (embedding-based)
  Layer 3: Temporal patterns (trending detection)
  Layer 4: Category grouping
"""

import json
import os
import time
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
PHRASES_FILE = BASE_DIR / "data" / "phrases.json"

# ── Category mappings ────────────────────────────────────────────────────────

CATEGORY_MAP = {
    "academics": {
        "emoji": "🎓",
        "keywords": ["gpa", "grade", "retake", "appeal", "transcript", "standing",
                     "dean's list", "honors", "probation", "credit", "course",
                     "major", "minor", "prerequisite", "curriculum"],
    },
    "deadlines": {
        "emoji": "📅",
        "keywords": ["withdraw", "register", "drop", "deadline", "last day",
                     "enrollment", "add", "schedule", "calendar", "semester",
                     "when", "date", "time", "period"],
    },
    "violations": {
        "emoji": "⚠️",
        "keywords": ["plagiarism", "cheating", "conduct", "discipline", "integrity",
                     "violation", "sanction", "penalty", "academic dishonesty",
                     "fraud", "misconduct", "honor code"],
    },
    "financial": {
        "emoji": "💰",
        "keywords": ["aid", "scholarship", "refund", "tuition", "fee", "loan",
                     "financial", "payment", "cost", "work-study", "fafsa",
                     "grant", "stipend"],
    },
}


# ── Trie Node ────────────────────────────────────────────────────────────────

class TrieNode:
    __slots__ = ("children", "is_end", "phrase", "category", "click_count", "last_clicked")

    def __init__(self):
        self.children: Dict[str, TrieNode] = {}
        self.is_end = False
        self.phrase: Optional[str] = None
        self.category: str = "general"
        self.click_count: int = 0
        self.last_clicked: float = 0.0


class AutocompleteEngine:
    """Trie-based autocomplete with multi-layer ranking."""

    def __init__(self):
        self.root = TrieNode()
        self.phrases: List[Dict] = []
        self.click_log: List[Dict] = []
        self.trending_window = 7 * 24 * 3600  # 7 days in seconds
        self._initialized = False

    def initialize(self):
        """Load phrases and build trie."""
        if self._initialized:
            return

        self.phrases = self._generate_phrases()
        for p in self.phrases:
            self._insert(p["text"], p["category"], p.get("click_count", 0))

        # Try loading saved click data
        if PHRASES_FILE.exists():
            try:
                with open(PHRASES_FILE) as f:
                    saved = json.load(f)
                    for item in saved.get("clicks", []):
                        self._record_click_internal(item["text"])
            except Exception:
                pass

        self._initialized = True
        print(f"Autocomplete engine initialized: {len(self.phrases)} phrases")

    def _insert(self, phrase: str, category: str = "general", click_count: int = 0):
        """Insert a phrase into the trie."""
        node = self.root
        for char in phrase.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.phrase = phrase
        node.category = category
        node.click_count = click_count

    def _search_prefix(self, prefix: str) -> List[TrieNode]:
        """Find all phrases matching a prefix."""
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]

        # Collect all end nodes
        results = []
        stack = [node]
        while stack:
            current = stack.pop()
            if current.is_end:
                results.append(current)
            stack.extend(current.children.values())
        return results

    def suggest(self, prefix: str, limit: int = 5, context: str = None) -> List[Dict]:
        """Get ranked suggestions for a prefix."""
        self.initialize()

        if len(prefix.strip()) < 1:
            return self._get_popular(limit)

        # ── Layer 1: Trie prefix match ──────────────────────────────────
        nodes = self._search_prefix(prefix)

        if not nodes:
            # Fallback: fuzzy match against all phrases
            nodes = self._fuzzy_match(prefix)

        now = time.time()
        suggestions = []
        for node in nodes:
            score = 0.0

            # Layer 1: Frequency score
            freq_score = min(node.click_count / 100, 1.0)  # Normalize
            score += freq_score * 0.3

            # Layer 2: Prefix match quality
            if node.phrase:
                match_ratio = len(prefix) / len(node.phrase)
                score += match_ratio * 0.25

            # Layer 3: Temporal trending
            if node.last_clicked > 0:
                recency = max(0, 1 - (now - node.last_clicked) / self.trending_window)
                score += recency * 0.25

            # Layer 4: Category relevance (boost if context matches)
            if context:
                category_info = CATEGORY_MAP.get(node.category, {})
                keywords = category_info.get("keywords", [])
                if any(kw in context.lower() for kw in keywords):
                    score += 0.2

            is_trending = (
                node.click_count > 10
                and node.last_clicked > now - self.trending_window
            )

            emoji = "📄"
            for cat_name, cat_info in CATEGORY_MAP.items():
                if cat_name == node.category:
                    emoji = cat_info["emoji"]
                    break

            suggestions.append({
                "text": node.phrase,
                "category": node.category,
                "emoji": emoji,
                "confidence": round(score, 3),
                "trending": is_trending,
                "click_count": node.click_count,
            })

        # Sort by score descending
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        return suggestions[:limit]

    def _fuzzy_match(self, prefix: str) -> List[TrieNode]:
        """Fallback: match phrases containing the prefix anywhere."""
        results = []
        prefix_lower = prefix.lower()
        stack = [self.root]
        while stack:
            node = stack.pop()
            if node.is_end and node.phrase and prefix_lower in node.phrase.lower():
                results.append(node)
            stack.extend(node.children.values())
        return results[:20]  # Limit fuzzy results

    def _get_popular(self, limit: int = 5) -> List[Dict]:
        """Get most popular phrases."""
        self.initialize()
        popular = sorted(self.phrases, key=lambda x: x.get("click_count", 0), reverse=True)

        results = []
        for p in popular[:limit]:
            emoji = "📄"
            for cat_name, cat_info in CATEGORY_MAP.items():
                if cat_name == p["category"]:
                    emoji = cat_info["emoji"]
                    break

            results.append({
                "text": p["text"],
                "category": p["category"],
                "emoji": emoji,
                "confidence": 0.5,
                "trending": p.get("click_count", 0) > 10,
                "click_count": p.get("click_count", 0),
            })
        return results

    def record_click(self, phrase: str):
        """Record a user click on a suggestion (learning signal)."""
        self._record_click_internal(phrase)
        self._save_clicks()

    def _record_click_internal(self, phrase: str):
        """Update trie node with click data."""
        node = self.root
        for char in phrase.lower():
            if char not in node.children:
                return
            node = node.children[char]
        if node.is_end:
            node.click_count += 1
            node.last_clicked = time.time()

    def _save_clicks(self):
        """Persist click data."""
        try:
            PHRASES_FILE.parent.mkdir(parents=True, exist_ok=True)
            clicks = []
            stack = [self.root]
            while stack:
                node = stack.pop()
                if node.is_end and node.click_count > 0:
                    clicks.append({
                        "text": node.phrase,
                        "click_count": node.click_count,
                        "last_clicked": node.last_clicked,
                    })
                stack.extend(node.children.values())
            with open(PHRASES_FILE, "w") as f:
                json.dump({"clicks": clicks}, f)
        except Exception as exc:
            print(f"[WARN] Could not save click data: {exc}")

    @staticmethod
    def _categorize(phrase: str) -> str:
        """Determine category of a phrase."""
        phrase_lower = phrase.lower()
        for cat_name, cat_info in CATEGORY_MAP.items():
            if any(kw in phrase_lower for kw in cat_info["keywords"]):
                return cat_name
        return "general"

    def _generate_phrases(self) -> List[Dict]:
        """Generate the phrase database for autocomplete."""
        raw_phrases = [
            # ── Academics ───────────────────────────────────────────
            "What GPA do I need to remain in good academic standing?",
            "How is GPA calculated at Westbrook University?",
            "What is the minimum passing grade for major courses?",
            "How do I appeal a grade?",
            "Can I retake a course to improve my grade?",
            "What is the grade appeal process?",
            "How do I request a grade change?",
            "What is the incomplete grade policy?",
            "How do I request an incomplete grade?",
            "What is the Pass/Fail grading option?",
            "Can I switch a course to Pass/Fail?",
            "What GPA do I need for the Dean's List?",
            "What are academic honors requirements?",
            "How does academic probation work?",
            "What happens if my GPA falls below 2.0?",
            "What is the academic standing policy?",
            "How many credits do I need to graduate?",
            "What are the core curriculum requirements?",
            "How do I declare a major?",
            "Can I change my major?",
            "What are the prerequisite requirements?",
            "How do I get a prerequisite waiver?",
            "How do transfer credits work?",
            "What is the course load policy?",
            "How many courses can I take per semester?",
            "What is the maximum credit load?",
            "How do I get on the Dean's List?",
            "What are the graduation requirements?",
            "How do I apply for graduation?",
            "What is the transcript request process?",
            "How do I get an official transcript?",
            "What are the elective course guidelines?",

            # ── Deadlines ───────────────────────────────────────────
            "When is the last day to withdraw from a course?",
            "What is the course withdrawal deadline?",
            "When is the add/drop deadline?",
            "When can I register for next semester?",
            "What is the registration deadline?",
            "When is the tuition payment deadline?",
            "When is the last day to change grading option?",
            "What are the important academic deadlines?",
            "When does the withdrawal period end?",
            "When is the Pass/Fail declaration deadline?",
            "When is the grade appeal deadline?",
            "When are final exams?",
            "When do grades get posted?",
            "When is the medical leave application deadline?",
            "When is the scholarship application due?",
            "What is the makeup exam request deadline?",

            # ── Violations ──────────────────────────────────────────
            "What happens if I plagiarize?",
            "What is the academic integrity policy?",
            "What are the consequences of cheating?",
            "How does the disciplinary process work?",
            "What is considered academic dishonesty?",
            "Can I appeal a plagiarism charge?",
            "What is the student code of conduct?",
            "What happens if I violate the conduct code?",
            "What are the sanctions for academic dishonesty?",
            "Can I use AI tools for assignments?",
            "What is the AI usage policy?",
            "What are the citation guidelines?",
            "How does the disciplinary appeals process work?",
            "What is considered cheating on an exam?",
            "What happens on a first offense?",
            "What is the research integrity policy?",

            # ── Financial ───────────────────────────────────────────
            "How do I apply for financial aid?",
            "What is the scholarship eligibility criteria?",
            "How do I maintain my scholarship?",
            "What is the tuition refund policy?",
            "Can I get a refund if I withdraw?",
            "What is the financial aid appeals process?",
            "How does satisfactory academic progress affect aid?",
            "What are the student loan guidelines?",
            "How does work-study work?",
            "What happens to my aid if I drop below full-time?",
            "How do I apply for a scholarship?",
            "What is the financial aid eligibility policy?",
            "Can I appeal a financial aid suspension?",
            "What is the refund schedule for withdrawals?",
            "How do I reapply for financial aid?",
            "What happens to my scholarship if my GPA drops?",

            # ── Attendance & Exams ──────────────────────────────────
            "How many absences am I allowed per semester?",
            "What qualifies as an excused absence?",
            "How do I request an excused absence?",
            "What is the attendance policy?",
            "Can I attend class remotely?",
            "What is the remote participation policy?",
            "What is the tardiness policy?",
            "How do I get a makeup exam?",
            "What is the final exam policy?",
            "Can I reschedule a final exam?",
            "What if I have three exams in one day?",
            "What is the exam proctoring policy?",
            "How do I get exam accommodations?",
            "What is the online exam policy?",
            "What happens if I miss a final exam?",
            "How do I request a religious holiday absence?",
            "What is the attendance appeals process?",

            # ── Withdrawal & Leave ──────────────────────────────────
            "How do I withdraw from a course?",
            "What is the difference between withdrawal and drop?",
            "How do I apply for medical leave?",
            "What is the medical leave of absence policy?",
            "Can I take a leave of absence?",
            "How do I return from a leave of absence?",
            "What is the administrative withdrawal policy?",
            "What is the military leave policy?",
            "Does withdrawal affect my GPA?",
            "Can I get a refund after withdrawing?",
            "What shows on my transcript after withdrawal?",
            "How long can a medical leave last?",
            "What documentation do I need for medical leave?",
            "What is the return from leave procedure?",
            "Can I withdraw after the deadline?",

            # ── Misc / Procedural ───────────────────────────────────
            "Who do I contact about academic policies?",
            "Where is the Office of Academic Affairs?",
            "How do I file a complaint?",
            "What support services are available?",
            "How do I contact my academic advisor?",
            "What is the campus safety policy?",
            "How do I request disability accommodations?",
            "What are the behavioral intervention procedures?",

            # ── Comparison queries ──────────────────────────────────
            "What is the difference between withdrawal and drop?",
            "What is the difference between probation and suspension?",
            "What is the difference between excused and unexcused absence?",
            "Compare Pass/Fail and letter grading",
            "What is the difference between academic warning and probation?",
            "Medical leave vs administrative withdrawal",
            "Transfer credits vs Westbrook credits",
        ]

        phrases = []
        seen = set()
        for text in raw_phrases:
            if text.lower() in seen:
                continue
            seen.add(text.lower())
            category = self._categorize(text)
            phrases.append({
                "text": text,
                "category": category,
                "click_count": 0,
            })

        return phrases


# ── Module-level singleton ───────────────────────────────────────────────────

_engine: Optional[AutocompleteEngine] = None


def get_engine() -> AutocompleteEngine:
    global _engine
    if _engine is None:
        _engine = AutocompleteEngine()
        _engine.initialize()
    return _engine
