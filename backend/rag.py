"""
CampusRule AI v2.0 — RAG (Retrieval-Augmented Generation) module.

Integrates with Ollama for local LLM inference.
Handles: prompt engineering, streaming generation, intent detection,
entity extraction, follow-up suggestions, and confidence scoring.
"""

import json
import os
import re
import time
from typing import AsyncGenerator, Dict, List, Optional, Tuple

import httpx
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma:7b")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_TOP_P = float(os.getenv("LLM_TOP_P", "0.9"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "512"))

# ── System Prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are CampusRule AI, an expert academic policy assistant for Westbrook University. 
Your role is to help students, faculty, and staff understand university policies accurately.

RULES:
1. ONLY answer based on the provided policy context. Never make up information.
2. If the context doesn't contain enough information, say so clearly.
3. Cite specific policy documents, sections, and page numbers when possible.
4. Use clear, concise language that students can easily understand.
5. For procedures, provide step-by-step instructions.
6. For deadlines, highlight specific dates and timeframes.
7. For eligibility questions, give clear yes/no answers with conditions.
8. If a question is ambiguous, ask for clarification.
9. Always be helpful and professional.
10. Format your response with markdown when it improves readability."""

# ── Intent Detection ─────────────────────────────────────────────────────────

INTENT_PATTERNS = {
    "eligibility": [
        r"\b(can i|am i|eligible|allowed|permitted|qualify|qualified)\b",
        r"\b(do i need|is it possible|may i)\b",
    ],
    "deadline": [
        r"\b(when|deadline|due date|last day|by when|how long|timeline)\b",
        r"\b(before|after|until|semester end)\b",
    ],
    "procedure": [
        r"\b(how (do|can|to)|steps|process|procedure|apply|submit|request|file)\b",
        r"\b(what do i need to|where do i)\b",
    ],
    "comparison": [
        r"\b(vs|versus|difference|compare|between|or)\b",
        r"\b(which is better|what.s the difference)\b",
    ],
    "rule": [
        r"\b(what is|what are|policy|rule|requirement|regulation|standard)\b",
        r"\b(how (many|much)|minimum|maximum|limit)\b",
    ],
}


def detect_intent(query: str) -> str:
    """Detect the intent type of a user query."""
    query_lower = query.lower()
    scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        for pattern in patterns:
            if re.search(pattern, query_lower):
                score += 1
        scores[intent] = score

    if not any(scores.values()):
        return "general"

    return max(scores, key=scores.get)


# ── Entity Extraction ────────────────────────────────────────────────────────

def extract_entities(query: str) -> Dict[str, List[str]]:
    """Extract named entities from the query."""
    entities = {"events": [], "values": [], "roles": []}

    # Events
    event_patterns = [
        r"\b(exam|examination|test|quiz)\b",
        r"\b(course|class|lecture|seminar)\b",
        r"\b(withdrawal|drop|leave|absence)\b",
        r"\b(grade|gpa|transcript)\b",
        r"\b(scholarship|financial aid|loan)\b",
        r"\b(appeal|petition|request)\b",
        r"\b(graduation|commencement)\b",
        r"\b(registration|enrollment)\b",
    ]
    for pattern in event_patterns:
        matches = re.findall(pattern, query.lower())
        entities["events"].extend(matches)

    # Values
    value_patterns = [
        r"\b(GPA\s*\d+\.?\d*)\b",
        r"\b(\d+\.?\d*\s*GPA)\b",
        r"\b(\d+\s*credit[s]?)\b",
        r"\b(spring|fall|summer|winter)\s*(semester|term|quarter)?\b",
        r"\b(\d+\s*%)\b",
        r"\b(\d+\s*(days?|weeks?|months?|hours?))\b",
    ]
    for pattern in value_patterns:
        matches = re.findall(pattern, query, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                entities["values"].append(match[0])
            else:
                entities["values"].append(match)

    # Roles
    role_patterns = [
        r"\b(student|undergraduate|graduate|freshman|sophomore|junior|senior)\b",
        r"\b(faculty|professor|instructor|advisor|dean)\b",
        r"\b(international|transfer|part.time|full.time)\b",
    ]
    for pattern in role_patterns:
        matches = re.findall(pattern, query.lower())
        entities["roles"].extend(matches)

    return entities


# ── Follow-up Generation ────────────────────────────────────────────────────

FOLLOW_UP_TEMPLATES = {
    "eligibility": [
        "What are the specific requirements for this?",
        "What happens if I don't meet the criteria?",
        "Is there an appeal process?",
    ],
    "deadline": [
        "What happens if I miss this deadline?",
        "Can I request an extension?",
        "What documentation do I need?",
    ],
    "procedure": [
        "How long does this process take?",
        "Who should I contact for help?",
        "What documents do I need to submit?",
    ],
    "comparison": [
        "Which option is better for my situation?",
        "What are the GPA implications of each?",
        "Can I change my decision later?",
    ],
    "rule": [
        "Are there any exceptions to this rule?",
        "How is this enforced?",
        "What are the consequences of violation?",
    ],
    "general": [
        "Can you explain this in more detail?",
        "Where can I find the full policy document?",
        "Who should I contact for more information?",
    ],
}


def generate_follow_ups(query: str, answer: str, intent: str, chunks: List[Dict]) -> List[str]:
    """Generate smart follow-up suggestions based on context."""
    follow_ups = []

    # Get template follow-ups based on intent
    templates = FOLLOW_UP_TEMPLATES.get(intent, FOLLOW_UP_TEMPLATES["general"])
    follow_ups.extend(templates[:2])

    # Add context-specific follow-ups based on mentioned topics
    query_lower = query.lower()
    if "gpa" in query_lower or "grade" in query_lower:
        follow_ups.append("How is GPA calculated at Westbrook?")
    if "withdrawal" in query_lower or "drop" in query_lower:
        follow_ups.append("What is the tuition refund schedule for withdrawals?")
    if "exam" in query_lower:
        follow_ups.append("What are the makeup exam procedures?")
    if "absence" in query_lower or "attendance" in query_lower:
        follow_ups.append("What qualifies as an excused absence?")
    if "plagiarism" in query_lower or "cheating" in query_lower:
        follow_ups.append("What are the penalties for academic dishonesty?")
    if "scholarship" in query_lower or "financial" in query_lower:
        follow_ups.append("How do I maintain my scholarship eligibility?")

    # Deduplicate and limit
    seen = set()
    unique = []
    for f in follow_ups:
        if f.lower() not in seen:
            seen.add(f.lower())
            unique.append(f)
    return unique[:3]


# ── Confidence Scoring ───────────────────────────────────────────────────────

def calculate_confidence(chunks: List[Dict]) -> float:
    """Calculate overall confidence based on chunk relevance scores."""
    if not chunks:
        return 0.0

    scores = [c.get("score", 0.0) for c in chunks[:3]]
    if not scores:
        return 0.0

    # Weighted average: first chunk matters most
    weights = [0.5, 0.3, 0.2][:len(scores)]
    weighted_sum = sum(s * w for s, w in zip(scores, weights))
    total_weight = sum(weights)

    confidence = weighted_sum / total_weight

    # Scale to 0-100 range (FAISS cosine sim is typically 0.3-0.9)
    confidence = min(max((confidence - 0.2) / 0.6, 0.0), 1.0) * 100

    return round(confidence, 1)


# ── Ollama Integration ───────────────────────────────────────────────────────

def _build_prompt(query: str, context: str, conversation_history: List[Dict] = None, intent: str = "general") -> str:
    """Build the full prompt with system instructions, context, and query."""

    intent_instructions = {
        "eligibility": "Provide a clear yes/no answer with specific conditions and requirements.",
        "deadline": "Highlight specific dates, timeframes, and deadlines. Be precise about when things are due.",
        "procedure": "Provide step-by-step instructions in numbered format. Be specific about forms and offices.",
        "comparison": "Create a clear comparison highlighting key differences and similarities.",
        "rule": "State the rule clearly, then explain its implications and any exceptions.",
        "general": "Provide a comprehensive and helpful answer.",
    }

    intent_note = intent_instructions.get(intent, intent_instructions["general"])

    history_text = ""
    if conversation_history:
        recent = conversation_history[-4:]  # Last 4 messages for context
        parts = []
        for msg in recent:
            role = "Student" if msg.get("role") == "user" else "CampusRule AI"
            parts.append(f"{role}: {msg.get('content', '')[:200]}")
        history_text = f"\n\nPrevious conversation:\n" + "\n".join(parts)

    prompt = f"""{SYSTEM_PROMPT}

INTENT: {intent} — {intent_note}

POLICY CONTEXT (use ONLY this information to answer):
{context}
{history_text}

Student's question: {query}

Provide a clear, accurate answer based ONLY on the policy context above. If the context doesn't fully answer the question, say what you can and note what information is missing."""

    return prompt


async def generate_answer(
    query: str,
    context: str,
    chunks: List[Dict],
    conversation_history: List[Dict] = None,
    intent: str = "general",
) -> Dict:
    """Generate a non-streaming answer from Ollama."""
    prompt = _build_prompt(query, context, conversation_history, intent)

    start_time = time.time()

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": LLM_TEMPERATURE,
                        "top_p": LLM_TOP_P,
                        "num_predict": LLM_MAX_TOKENS,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()

        answer = data.get("response", "").strip()
        thinking_time = round(time.time() - start_time, 2)
        confidence = calculate_confidence(chunks)
        follow_ups = generate_follow_ups(query, answer, intent, chunks)

        return {
            "answer": answer,
            "confidence": confidence,
            "thinking_time": thinking_time,
            "follow_ups": follow_ups,
            "intent": intent,
            "sources": chunks,
            "cited_documents": list(dict.fromkeys(c["document"] for c in chunks)),
        }

    except httpx.ConnectError:
        return _fallback_answer(query, chunks, "Ollama is not running. Using extractive fallback.")
    except Exception as exc:
        print(f"[WARN] LLM generation error: {exc}")
        return _fallback_answer(query, chunks, str(exc))


async def generate_answer_stream(
    query: str,
    context: str,
    chunks: List[Dict],
    conversation_history: List[Dict] = None,
    intent: str = "general",
) -> AsyncGenerator[str, None]:
    """Stream answer tokens from Ollama for real-time display."""
    prompt = _build_prompt(query, context, conversation_history, intent)

    start_time = time.time()
    confidence = calculate_confidence(chunks)
    follow_ups = generate_follow_ups(query, answer="", intent=intent, chunks=chunks)
    cited_docs = list(dict.fromkeys(c["document"] for c in chunks))

    # Send metadata first
    meta = {
        "type": "meta",
        "confidence": confidence,
        "intent": intent,
        "sources": [
            {
                "text": c["text"][:200],
                "document": c["document"],
                "page": c["page"],
                "category": c["category"],
                "section": c["section"],
                "score": c["score"],
            }
            for c in chunks
        ],
        "cited_documents": cited_docs,
    }
    yield f"data: {json.dumps(meta)}\n\n"

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": LLM_TEMPERATURE,
                        "top_p": LLM_TOP_P,
                        "num_predict": LLM_MAX_TOKENS,
                    },
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            token = data.get("response", "")
                            if token:
                                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue

    except httpx.ConnectError:
        # Fallback: stream the extractive QA answer
        fallback = _fallback_answer(query, chunks, "Ollama is not running.")
        for word in fallback["answer"].split():
            yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"

    except Exception as exc:
        print(f"[WARN] Stream error: {exc}")
        yield f"data: {json.dumps({'type': 'error', 'content': str(exc)})}\n\n"

    # Send completion
    thinking_time = round(time.time() - start_time, 2)
    done = {
        "type": "done",
        "thinking_time": thinking_time,
        "follow_ups": follow_ups,
    }
    yield f"data: {json.dumps(done)}\n\n"


def _fallback_answer(query: str, chunks: List[Dict], error_msg: str = "") -> Dict:
    """Fallback answer using extractive QA when Ollama is unavailable."""
    confidence = calculate_confidence(chunks)
    intent = detect_intent(query)
    follow_ups = generate_follow_ups(query, "", intent, chunks)

    if chunks:
        # Try extractive QA
        try:
            from retrieval import _get_qa_pipeline
            context = " ".join(c["text"] for c in chunks[:3])[:3000]
            qa = _get_qa_pipeline()
            result = qa(question=query, context=context, max_answer_len=250, handle_impossible_answer=True)
            answer = result["answer"].strip()
            qa_confidence = float(result["score"])

            if not answer or qa_confidence < 0.05:
                answer = chunks[0]["text"][:400]
        except Exception:
            answer = chunks[0]["text"][:400]
    else:
        answer = "I couldn't find relevant information for your query."

    note = ""
    if error_msg:
        note = f"\n\n*Note: Using extractive QA fallback. {error_msg}*"

    return {
        "answer": answer + note,
        "confidence": confidence,
        "thinking_time": 0.0,
        "follow_ups": follow_ups,
        "intent": intent,
        "sources": chunks,
        "cited_documents": list(dict.fromkeys(c["document"] for c in chunks)),
    }


async def check_ollama_status() -> Dict:
    """Check if Ollama is running and the model is available."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            models = [m["name"] for m in data.get("models", [])]
            model_available = any(OLLAMA_MODEL in m for m in models)
            return {
                "ollama_running": True,
                "model_available": model_available,
                "model_name": OLLAMA_MODEL,
                "available_models": models,
            }
    except Exception:
        return {
            "ollama_running": False,
            "model_available": False,
            "model_name": OLLAMA_MODEL,
            "available_models": [],
        }
