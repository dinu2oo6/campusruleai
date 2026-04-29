# CampusRule AI

Semantic academic policy retrieval system for Westbrook University. Students and faculty ask natural-language questions; the system searches 48 official policy PDFs and extracts precise answers using FAISS + RoBERTa extractive QA — zero hallucination by design.

---

## Architecture

```
Query → sentence-transformers (MiniLM) → FAISS (cosine) → Top-5 chunks
      → deepset/roberta-base-squad2 (extractive QA) → Grounded answer
```

- **Embeddings**: `all-MiniLM-L6-v2` (384-dim, ~80 MB)
- **Vector index**: FAISS `IndexFlatIP` (inner product on L2-normalised vectors = cosine similarity)
- **QA model**: `deepset/roberta-base-squad2` — extracts an exact span from the source text; cannot invent content
- **PDF parsing**: `pdfplumber` with sliding-window chunking (400 words, 80-word overlap)
- **No external API key required**

---

## Quick Start

### 1. Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate the 48 policy PDFs
python pdf_generator.py

# Start the API server
uvicorn main:app --reload --port 8000
```

The first startup will:
1. Parse all PDFs and chunk them (~480 chunks)
2. Download `all-MiniLM-L6-v2` (~80 MB) and `roberta-base-squad2` (~500 MB) on first run
3. Build the FAISS index and save it to `data/index.faiss`
4. Subsequent startups load the cached index (fast)

### 2. Frontend

```bash
cd frontend

npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/search` | Semantic search + extractive QA |
| `GET`  | `/api/documents` | List all indexed documents |
| `POST` | `/api/upload` | Upload a new PDF (triggers re-index) |
| `DELETE` | `/api/documents/{filename}` | Delete a document |
| `GET`  | `/api/health` | Health check |

### Search request

```json
{ "query": "How many absences am I allowed?", "top_k": 5 }
```

### Search response

```json
{
  "answer": "Students are permitted a maximum of 3 unexcused absences per semester in any single course.",
  "confidence": 0.87,
  "source_chunks": [
    {
      "text": "...",
      "document": "class_attendance_policy.pdf",
      "page": 1,
      "category": "attendance",
      "section": "Attendance Requirements",
      "score": 0.91
    }
  ],
  "cited_documents": ["class_attendance_policy.pdf"]
}
```

---

## Document Categories (48 PDFs)

| Category | Color | Documents |
|----------|-------|-----------|
| Grading | Blue | Undergraduate Grading, GPA Appeals, Grade Change, Academic Standing, Incomplete Grade, Pass/Fail |
| Attendance | Green | Class Attendance, Excused Absences, Remote Participation, Tardiness, Appeals, Religious Holiday |
| Exams | Purple | Final Exams, Makeup Exams, Proctoring, Accommodations, Scheduling Conflicts, Online Exams |
| Disciplinary | Red | Code of Conduct, Disciplinary Procedures, Appeals, Sanctions, Behavioral Intervention, Campus Safety |
| Integrity | Orange | Academic Honesty, Plagiarism, Cheating/Fraud, AI Usage, Citation Guidelines, Research Integrity |
| Financial Aid | Yellow | Eligibility, Scholarship Application, Student Loans, SAP, Appeals, Work-Study |
| Prerequisites | Teal | Core Curriculum, Prerequisite Waivers, Electives, Transfer Credits, Course Load, Major Declaration |
| Withdrawal | Pink | Course Withdrawal, Medical Leave, Tuition Refund, Admin Withdrawal, Return from Leave, Military Leave |

---

## Project Structure

```
campusai/
├── backend/
│   ├── main.py              # FastAPI app with all endpoints
│   ├── retrieval.py         # FAISS index, embedding, QA pipeline
│   ├── pdf_generator.py     # Generates 48 realistic policy PDFs
│   ├── requirements.txt
│   ├── .env                 # Configuration
│   └── data/
│       ├── documents/       # PDF files (generated)
│       ├── index.faiss      # FAISS index (auto-created)
│       └── metadata.json    # Chunk metadata (auto-created)
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── SearchBar.jsx        # Query input + suggestions
    │   │   ├── ResultCard.jsx       # Answer + expandable source chunks
    │   │   ├── DocumentBrowser.jsx  # Sidebar document browser
    │   │   └── QueryHistory.jsx     # Chat-like query history
    │   ├── pages/
    │   │   └── Dashboard.jsx        # Main layout + state management
    │   ├── App.jsx
    │   └── index.css                # Tailwind + custom styles
    ├── package.json
    ├── vite.config.js
    └── tailwind.config.js
```

---

## Requirements

- Python 3.10+
- Node.js 18+
- ~1 GB disk space (ML models cached by HuggingFace on first run)
- 4 GB RAM recommended (models load into memory)
