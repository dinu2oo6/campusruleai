"""
CampusRule AI v2.0 — Retrieval module.

Hybrid search: FAISS semantic similarity + BM25 keyword matching.
Re-ranking of retrieved chunks by combined relevance score.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import faiss
import pdfplumber
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi

load_dotenv()

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / os.getenv("DOCS_DIR", "data/documents")
INDEX_DIR = BASE_DIR / os.getenv("INDEX_DIR", "data")
INDEX_FILE = INDEX_DIR / "index.faiss"
METADATA_FILE = INDEX_DIR / "metadata.json"

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 400))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 80))
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
QA_MODEL_NAME = os.getenv("QA_MODEL", "deepset/roberta-base-squad2")

CATEGORY_KEYWORDS = {
    "grading": ["grading", "gpa", "grade_change", "academic_standing", "incomplete", "pass_fail", "letter_grade"],
    "attendance": ["attendance", "absence", "tardiness", "remote_participation", "religious_holiday"],
    "exam": ["exam", "examination", "makeup", "proctoring", "accommodation", "scheduling", "online_exam"],
    "disciplinary": ["conduct", "disciplinary", "sanctions", "behavioral", "safety", "violation"],
    "integrity": ["integrity", "plagiarism", "cheating", "ai_usage", "citation", "research_integrity"],
    "financial": ["financial", "scholarship", "loan", "satisfactory_academic", "work_study", "aid"],
    "prerequisites": ["prerequisite", "curriculum", "elective", "transfer_credit", "course_load", "major_declaration"],
    "withdrawal": ["withdrawal", "leave_of_absence", "refund", "military_leave", "return_from_leave", "administrative_withdrawal"],
}

CATEGORY_EMOJI = {
    "grading": "🎓",
    "attendance": "📅",
    "exam": "📝",
    "disciplinary": "⚠️",
    "integrity": "⚠️",
    "financial": "💰",
    "prerequisites": "📚",
    "withdrawal": "📅",
    "general": "📄",
}

# ── Lazy-loaded singletons ───────────────────────────────────────────────────

_embedding_model = None
_qa_pipeline = None
_index: Optional[faiss.Index] = None
_metadata: List[Dict] = []
_bm25: Optional[BM25Okapi] = None
_bm25_corpus: List[List[str]] = []


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def _get_qa_pipeline():
    global _qa_pipeline
    if _qa_pipeline is None:
        from transformers import pipeline
        print(f"Loading QA model: {QA_MODEL_NAME}")
        _qa_pipeline = pipeline(
            "question-answering",
            model=QA_MODEL_NAME,
            tokenizer=QA_MODEL_NAME,
        )
    return _qa_pipeline


def _build_bm25():
    """Build BM25 index from metadata for keyword matching."""
    global _bm25, _bm25_corpus
    if not _metadata:
        return
    _bm25_corpus = [doc["text"].lower().split() for doc in _metadata]
    _bm25 = BM25Okapi(_bm25_corpus)
    print(f"BM25 index built: {len(_bm25_corpus)} documents")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_category(filename: str) -> str:
    name = filename.lower().replace("-", "_").replace(" ", "_")
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in name for kw in keywords):
            return category
    return "general"


def _extract_section_title(text: str) -> str:
    lines = text.strip().split("\n")
    for line in lines[:3]:
        line = line.strip()
        if line and 10 < len(line) < 120:
            return line[:100]
    return text[:60].strip()


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i: i + chunk_size]
        chunk = " ".join(chunk_words)
        if len(chunk.strip()) > 80:
            chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def _parse_pdf(pdf_path: Path) -> List[Dict]:
    records = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                raw = page.extract_text()
                if not raw:
                    continue
                text = re.sub(r"[ \t]+", " ", raw).strip()
                chunks = _chunk_text(text)
                for chunk in chunks:
                    records.append({
                        "text": chunk,
                        "document": pdf_path.name,
                        "page": page_num,
                        "category": _get_category(pdf_path.name),
                        "section": _extract_section_title(chunk),
                    })
    except Exception as exc:
        print(f"[WARN] Could not parse {pdf_path.name}: {exc}")
    return records


# ── Index Management ─────────────────────────────────────────────────────────

def build_index() -> None:
    global _index, _metadata

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    pdf_files = sorted(DOCS_DIR.glob("*.pdf"))
    if not pdf_files:
        print("[WARN] No PDF files found in", DOCS_DIR)
        return

    print(f"Indexing {len(pdf_files)} documents...")
    all_records: List[Dict] = []
    for pdf_path in pdf_files:
        records = _parse_pdf(pdf_path)
        all_records.extend(records)
        print(f"  {pdf_path.name}: {len(records)} chunks")

    if not all_records:
        print("[WARN] No text extracted from PDFs.")
        return

    model = _get_embedding_model()
    texts = [r["text"] for r in all_records]
    print(f"Embedding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True, batch_size=64)
    embeddings = embeddings.astype(np.float32)

    dim = embeddings.shape[1]
    idx = faiss.IndexFlatIP(dim)
    idx.add(embeddings)

    faiss.write_index(idx, str(INDEX_FILE))
    with open(METADATA_FILE, "w") as f:
        json.dump(all_records, f, indent=2)

    _index = idx
    _metadata = all_records
    _build_bm25()
    print(f"Index built: {len(all_records)} chunks from {len(pdf_files)} documents.")


def load_index() -> bool:
    global _index, _metadata
    if INDEX_FILE.exists() and METADATA_FILE.exists():
        try:
            _index = faiss.read_index(str(INDEX_FILE))
            with open(METADATA_FILE) as f:
                _metadata = json.load(f)
            _build_bm25()
            print(f"Index loaded: {len(_metadata)} chunks.")
            return True
        except Exception as exc:
            print(f"[WARN] Failed to load index: {exc}")
    return False


# ── Hybrid Search ────────────────────────────────────────────────────────────

def hybrid_search(query: str, top_k: int = 5, semantic_weight: float = 0.7) -> List[Dict]:
    """
    Perform hybrid search combining FAISS semantic search and BM25 keyword matching.
    Results are re-ranked by combined score.
    """
    global _index, _metadata, _bm25

    if _index is None or not _metadata:
        if not load_index():
            build_index()

    if _index is None or not _metadata:
        return []

    # ── Semantic search via FAISS ────────────────────────────────────────
    model = _get_embedding_model()
    query_vec = model.encode([query], normalize_embeddings=True).astype(np.float32)

    k_search = min(top_k * 3, len(_metadata))
    faiss_scores, faiss_indices = _index.search(query_vec, k_search)

    # Normalize FAISS scores to 0-1 range
    faiss_results = {}
    max_faiss = max(faiss_scores[0]) if len(faiss_scores[0]) > 0 else 1.0
    for score, idx in zip(faiss_scores[0], faiss_indices[0]):
        if idx < 0 or idx >= len(_metadata):
            continue
        normalized = float(score) / max(max_faiss, 1e-6)
        faiss_results[idx] = max(normalized, 0.0)

    # ── BM25 keyword search ─────────────────────────────────────────────
    bm25_results = {}
    if _bm25 is not None:
        query_tokens = query.lower().split()
        bm25_scores = _bm25.get_scores(query_tokens)
        max_bm25 = max(bm25_scores) if len(bm25_scores) > 0 else 1.0
        # Get top indices
        top_bm25_indices = np.argsort(bm25_scores)[::-1][:k_search]
        for idx in top_bm25_indices:
            if bm25_scores[idx] > 0:
                normalized = float(bm25_scores[idx]) / max(max_bm25, 1e-6)
                bm25_results[int(idx)] = normalized

    # ── Combine and re-rank ─────────────────────────────────────────────
    all_indices = set(faiss_results.keys()) | set(bm25_results.keys())
    combined_scores = []
    for idx in all_indices:
        sem_score = faiss_results.get(idx, 0.0)
        kw_score = bm25_results.get(idx, 0.0)
        combined = semantic_weight * sem_score + (1 - semantic_weight) * kw_score
        combined_scores.append((idx, combined, sem_score, kw_score))

    # Sort by combined score descending
    combined_scores.sort(key=lambda x: x[1], reverse=True)

    # Build result chunks
    results = []
    for idx, combined, sem_score, kw_score in combined_scores[:top_k]:
        record = dict(_metadata[idx])
        record["score"] = float(round(combined, 4))
        record["semantic_score"] = float(round(sem_score, 4))
        record["keyword_score"] = float(round(kw_score, 4))
        record["emoji"] = CATEGORY_EMOJI.get(record["category"], "📄")
        results.append(record)

    return results


def search(query: str, top_k: int = 5) -> Dict:
    """Legacy search endpoint — backward compatible with v1.0."""
    global _index, _metadata

    if _index is None or not _metadata:
        if not load_index():
            build_index()

    if _index is None or not _metadata:
        return {
            "answer": "The document index is not available. Please ensure PDFs are present and the index is built.",
            "confidence": 0.0,
            "source_chunks": [],
            "cited_documents": [],
        }

    model = _get_embedding_model()
    query_vec = model.encode([query], normalize_embeddings=True).astype(np.float32)

    k = min(top_k, len(_metadata))
    scores, indices = _index.search(query_vec, k)

    source_chunks = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(_metadata):
            continue
        record = dict(_metadata[idx])
        record["score"] = round(float(score), 4)
        source_chunks.append(record)

    if not source_chunks:
        return {
            "answer": "No relevant information found for your query.",
            "confidence": 0.0,
            "source_chunks": [],
            "cited_documents": [],
        }

    # Build context from top-3 chunks for QA
    context = " ".join(c["text"] for c in source_chunks[:3])
    context = context[:3000]  # roberta max context window guard

    try:
        qa = _get_qa_pipeline()
        result = qa(question=query, context=context, max_answer_len=250, handle_impossible_answer=True)
        answer = result["answer"].strip()
        confidence = float(result["score"])

        # If model returns empty or no-answer token, fall back to best chunk excerpt
        if not answer or confidence < 0.05:
            answer = source_chunks[0]["text"][:400]
            confidence = float(source_chunks[0]["score"])
    except Exception as exc:
        print(f"[WARN] QA pipeline error: {exc}")
        answer = source_chunks[0]["text"][:400]
        confidence = float(source_chunks[0]["score"])

    cited_documents = list(dict.fromkeys(c["document"] for c in source_chunks))

    return {
        "answer": answer,
        "confidence": round(confidence, 4),
        "source_chunks": source_chunks,
        "cited_documents": cited_documents,
    }


def get_all_documents() -> List[Dict]:
    if not _metadata:
        load_index()

    seen: Dict[str, Dict] = {}
    for chunk in _metadata:
        name = chunk["document"]
        if name not in seen:
            doc_path = DOCS_DIR / name
            size_bytes = doc_path.stat().st_size if doc_path.exists() else 0
            seen[name] = {
                "name": name,
                "category": chunk["category"],
                "size_bytes": size_bytes,
                "size_kb": round(size_bytes / 1024, 1),
                "chunk_count": 0,
                "max_page": 0,
            }
        seen[name]["chunk_count"] += 1
        seen[name]["max_page"] = max(seen[name]["max_page"], chunk.get("page", 1))

    docs = sorted(seen.values(), key=lambda d: (d["category"], d["name"]))
    return docs


def get_chunks_for_context(query: str, top_k: int = 5) -> Tuple[List[Dict], str]:
    """
    Retrieve top-k chunks and build a context string for RAG.
    Returns (chunks, context_string).
    """
    chunks = hybrid_search(query, top_k=top_k)
    if not chunks:
        return [], ""

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk["document"].replace(".pdf", "").replace("_", " ").title()
        context_parts.append(
            f"[Source {i}: {source}, Section: {chunk['section']}, Page {chunk['page']}]\n{chunk['text']}"
        )

    context = "\n\n".join(context_parts)
    return chunks, context


def get_all_categories() -> Dict[str, int]:
    """Return category counts from indexed metadata."""
    if not _metadata:
        load_index()
    counts = {}
    for chunk in _metadata:
        cat = chunk.get("category", "general")
        counts[cat] = counts.get(cat, 0) + 1
    return counts
