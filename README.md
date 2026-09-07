# SIH26108: AI-Powered Recommendation Engine for Applicable Indian Standards

> **Smart India Hackathon 2026**  
> Problem Statement: **SIH26108**  
> Domain: Public Procurement / Bureau of Indian Standards (BIS) Quality Compliance

---

## 1. Overview
This project builds an intelligent recommendation and compliance engine for public procurement officials, tender scrutiny committees, and bidders. Given an unstructured technical procurement specification or draft tender clause, the system identifies applicable Indian Standards (IS), surfaces mandatory Quality Control Orders (QCOs), maps companion test/safety methods, and provides audit-ready technical justifications.

---

## 2. Architecture & Technology Stack (Locked)

- **Frontend:** React + Vite (Vanilla CSS, modern responsive design tokens)
- **Backend:** Python + FastAPI (asynchronous, typed Pydantic models)
- **Relational Metadata DB:** SQLite (`data/db/standards.db`)
- **Vector Database:** Qdrant (local embedded disk storage at `data/qdrant_storage` with zero external server dependencies, or remote URL)
- **Embedding Pipeline:** Free, local multilingual ONNX embedding model (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensions)
- **LLM Boundary:** Strictly constrained; never used as the source of truth for standard numbers or applicability.

---

## 3. Repository Structure

```
Standards-AI/
├── ARCHITECTURE.md          # Locked architectural specifications and pipeline contracts
├── DEVELOPMENT_RULES.md     # Inviolable development rules and constraints
├── PROJECT_CONTEXT.md       # Problem statement, personas, and system boundaries
├── PROJECT_STATE.md         # Active milestone tracker (Run 0, Run 1, etc.)
├── RUN_ROADMAP.md           # 9-run incremental implementation roadmap
├── RUN_1_REPORT.md          # Run 1 verification report and architecture summary
├── pytest.ini               # Pytest configuration
├── backend/                 # FastAPI service and data pipelines
│   ├── requirements.txt     # Python dependencies
│   ├── app/
│   │   ├── main.py          # FastAPI app entrypoint with CORS & lifespan
│   │   ├── core/            # Configuration & environment settings
│   │   ├── db/              # SQLite connection, schema, and seed script
│   │   ├── schemas/         # Pydantic request/response validation
│   │   └── services/        # Embedding, Qdrant vector store, and indexer
│   └── tests/               # Automated pytest suite (DB, Embedding, Qdrant, API)
├── frontend/                # React + Vite application
│   ├── package.json         # Frontend dependencies
│   ├── vite.config.js       # Vite configuration
│   ├── index.html           # SPA entrypoint with SEO metadata & Inter font
│   └── src/
│       ├── main.jsx         # React DOM mount
│       ├── App.jsx          # Search application container
│       ├── index.css        # Premium vanilla CSS styling
│       └── components/      # Header, SearchBar, ResultCard components
└── data/
    ├── raw/                 # Curated authoritative BIS seed dataset (JSON)
    ├── db/                  # SQLite database file (standards.db)
    └── qdrant_storage/      # Local Qdrant embedded vector storage
```

---

## 4. Quick Start: Developer Setup

Follow these exact steps to run the complete stack locally.

### Step 1: Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 2: Initialize SQLite Database & Seed BIS Standards
Seeds 15 authentic, authoritative Indian Standards with verified scopes and relationships:
```bash
python -m app.db.init_db
```
*(Run this command from inside the `backend/` directory, or set `PYTHONPATH=backend`)*

### Step 3: Index Standards into Local Qdrant
Generates 384-dimensional dense vectors using the local multilingual model and indexes them into Qdrant (`bis_standards` collection):
```bash
python -m app.services.indexer
```

### Step 4: Run Backend Automated Test Suite
Executes unit and integration tests for SQLite schema, embedding service, Qdrant retrieval, and FastAPI endpoints:
```bash
pytest backend/tests/ -v
```

### Step 5: Start the FastAPI Backend Server
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive API Docs: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/api/v1/health`
- Semantic Search API: `POST http://127.0.0.1:8000/api/v1/search`

### Step 6: Install Frontend Dependencies & Start React
In a new terminal:
```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```
Open your browser at:
```
http://127.0.0.1:5173/
```

---

## 5. End-to-End Verification Example

1. Open `http://127.0.0.1:5173/` in your browser.
2. Enter the tender specification:
   ```text
   12 mm TMT reinforcement bars for RCC construction
   ```
3. Click **Find Applicable Standards**.
4. The system retrieves **IS 1786:2008** (*High Strength Deformed Steel Bars and Wires for Concrete Reinforcement — Specification*) with a 61% semantic match, verified scope, and direct link to the official BIS portal.
5. Enter:
   ```text
   Industrial safety helmets for construction workers
   ```
6. The system retrieves **IS 2925:1984** (*Specification for Industrial Safety Helmets*) with a 78% semantic match.

---

## 6. Anti-Hallucination Invariant
The system adheres to strict grounding principles:
- No standard number or title is generated from LLM memory.
- Every result is retrieved directly from indexed official BIS scopes stored in SQLite and Qdrant.
- Semantic similarity scores denote relevance to the official scope and are explicitly tagged with an audit disclaimer clarifying that they do not constitute legal certification or formal procurement authority approval.

---

## 7. Run Status
- **RUN 0 (Project Foundation):** COMPLETED
- **RUN 1 (Core Semantic Standards Search MVP):** COMPLETED
- **RUN 2 (Ranking, Filtering & Explanations):** NOT STARTED
