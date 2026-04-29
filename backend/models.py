"""
Pydantic data models for CampusRule AI v2.0 API.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────────

class IntentType(str, Enum):
    ELIGIBILITY = "eligibility"
    DEADLINE = "deadline"
    PROCEDURE = "procedure"
    RULE = "rule"
    COMPARISON = "comparison"
    GENERAL = "general"


class CategoryType(str, Enum):
    ACADEMICS = "academics"
    DEADLINES = "deadlines"
    VIOLATIONS = "violations"
    FINANCIAL = "financial"
    GENERAL = "general"


class ExportFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MARKDOWN = "md"


# ── Chat ─────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    conversation_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    stream: bool = True


class SourceChunk(BaseModel):
    text: str
    document: str
    page: int
    category: str
    section: str
    score: float
    subsection: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk] = []
    confidence: float = 0.0
    follow_ups: List[str] = []
    thinking_time: float = 0.0
    intent: str = "general"
    conversation_id: str = ""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cited_documents: List[str] = []


# ── Autocomplete ─────────────────────────────────────────────────────────────

class AutocompleteRequest(BaseModel):
    prefix: str = Field(..., min_length=1, max_length=200)
    context: Optional[str] = None
    user_major: Optional[str] = None
    limit: int = Field(default=5, ge=1, le=10)


class SuggestionItem(BaseModel):
    text: str
    category: str
    emoji: str = "🎓"
    confidence: float = 0.0
    trending: bool = False
    click_count: int = 0


class AutocompleteResponse(BaseModel):
    suggestions: List[SuggestionItem] = []
    query_time_ms: float = 0.0


# ── Conversation ─────────────────────────────────────────────────────────────

class ConversationMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # "user" or "assistant"
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    sources: List[SourceChunk] = []
    confidence: float = 0.0
    follow_ups: List[str] = []
    intent: str = "general"


class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[ConversationMessage] = []
    created_at: str = ""
    updated_at: str = ""
    title: str = ""


# ── Feedback ─────────────────────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    message_id: str
    conversation_id: str
    rating: int = Field(..., ge=1, le=5)
    helpful: bool = True
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    success: bool = True
    message: str = "Feedback saved successfully"


# ── Analytics ────────────────────────────────────────────────────────────────

class AnalyticsResponse(BaseModel):
    total_questions: int = 0
    avg_response_time: float = 0.0
    avg_confidence: float = 0.0
    top_policies: List[Dict[str, Any]] = []
    trending_questions: List[Dict[str, Any]] = []
    questions_by_category: Dict[str, int] = {}
    questions_over_time: List[Dict[str, Any]] = []
    peak_hours: List[Dict[str, Any]] = []
    satisfaction_rating: float = 0.0


# ── Export ────────────────────────────────────────────────────────────────────

class ExportRequest(BaseModel):
    conversation_id: str
    format: ExportFormat = ExportFormat.TXT


class ExportResponse(BaseModel):
    filename: str
    content_type: str
    download_url: str


# ── Search (backward compatibility) ──────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: Optional[int] = Field(default=5, ge=1, le=10)


class SearchResponse(BaseModel):
    answer: str
    confidence: float
    source_chunks: list
    cited_documents: list


# ── Documents ────────────────────────────────────────────────────────────────

class DocumentInfo(BaseModel):
    name: str
    category: str
    size_bytes: int
    size_kb: float
    chunk_count: int
    max_page: int
