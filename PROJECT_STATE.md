# Project State: SIH26108

## Current Status
- **Run 0 (Project Foundation and Environment):** COMPLETED
- **Run 1 (Core Semantic Standards Search MVP):** COMPLETED
- **Pre-Run-2 Data Quality & Evidence Cleanup:** COMPLETED
- **Run 2A (Dynamic Results & Metadata-Enhanced Ranking):** COMPLETED
- **Run 2B (Explainability & Relevance Tiers):** COMPLETED
- **Run 3 to Run 8:** NOT STARTED

---

## Functional Status (Run 2A + Run 2B Completed)
- Dynamic search results implemented: returns only results above configurable relevance threshold (`settings.DEFAULT_SCORE_THRESHOLD = 0.38` or user query threshold).
- Hybrid ranking implemented preserving dense semantic search as primary signal (75% weight) boosted by authentic BIS metadata (title, scope, category, keywords, standard number - 25% weight).
- Verified that IS 1786:2008 ranks decisively above IS 2062:2011 for `"Fe 500 ribbed steel bars for reinforced concrete columns"`.
- Explainability engine implemented: generates concise 1-2 sentence "Why this standard?" justifications strictly citing official BIS scope, title, category, and matching keywords without hallucinating regulatory claims.
- Relevance labels (High, Medium, Low) calibrated and rendered in UI and API responses.
- 100% local operation: zero paid API dependencies, zero external cloud requirements.
- 18/18 automated backend tests passing (`pytest backend/tests/ -v`, 3.56s).

### Pre-Run-2 Cleanup Summary
- All unsupported regulatory/QCO/procurement claims removed from `source_evidence_note` fields in the seed dataset.
- Regulatory/QCO determination explicitly deferred to Run 5; no enforcement status is stored or displayed.
- Source URLs retained as BIS portal search references; none were fabricated.
- UI wording updated: "Semantic Match" → "Semantic Relevance", "Grounded in Verified BIS Scope" → "Based on Verified BIS Scope", "BIS Source Portal" → "BIS Reference Link".
- Configurable `limit` parameter added to the search API and exposed as a dropdown in the frontend (Top 5 / 10 / 15).
- `RUN_1_REPORT.md` updated with Section 8: Data Quality Notes documenting all changes.

---

## Deliverables Inventory

### 1. Data Layer
- Curated Authoritative Seed Dataset: [`data/raw/bis_seed_standards.json`](file:///c:/Standards-AI/data/raw/bis_seed_standards.json) (15 verified standards across structural steel, rebar, cement, concrete, piping, electrical cables, PPE, masonry).
- SQLite Database: [`data/db/standards.db`](file:///c:/Standards-AI/data/db/standards.db)
- Relational Schema & Seeding Script: [`backend/app/db/database.py`](file:///c:/Standards-AI/backend/app/db/database.py) and [`backend/app/db/init_db.py`](file:///c:/Standards-AI/backend/app/db/init_db.py).
- Tables: `standards`, `standard_relationships`, with indexes on standard numbers, categories, statuses, and foreign keys.

### 2. Embedding & Vector Retrieval Engine
- Clean Abstract Interface: [`backend/app/services/embedding.py`](file:///c:/Standards-AI/backend/app/services/embedding.py) (`BaseEmbeddingService`).
- Local Embedding Implementation: `FastEmbedService` (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensions, ONNX Runtime).
- Local Vector Store: [`backend/app/services/vector_store.py`](file:///c:/Standards-AI/backend/app/services/vector_store.py) (Qdrant collection `bis_standards`, cosine distance, local embedded disk storage at `data/qdrant_storage`).
- Vector Indexer Pipeline: [`backend/app/services/indexer.py`](file:///c:/Standards-AI/backend/app/services/indexer.py).

### 3. API Layer
- FastAPI Service: [`backend/app/main.py`](file:///c:/Standards-AI/backend/app/main.py).
- `GET /api/v1/health`: Operational health, standard count, vector collection status.
- `POST /api/v1/search`: Accepts technical specification, generates local dense vector, queries Qdrant, returns ranked standards with similarity score, scope, and source links.
- Pydantic Validation: [`backend/app/schemas/search.py`](file:///c:/Standards-AI/backend/app/schemas/search.py).

### 4. Frontend Application
- React + Vite SPA: [`frontend/`](file:///c:/Standards-AI/frontend).
- Modern design system with vanilla CSS: [`frontend/src/index.css`](file:///c:/Standards-AI/frontend/src/index.css).
- Interactive Components: [`Header.jsx`](file:///c:/Standards-AI/frontend/src/components/Header.jsx), [`SearchBar.jsx`](file:///c:/Standards-AI/frontend/src/components/SearchBar.jsx), [`ResultCard.jsx`](file:///c:/Standards-AI/frontend/src/components/ResultCard.jsx), [`App.jsx`](file:///c:/Standards-AI/frontend/src/App.jsx).
- Quick tender query chips, loading spinner, error banner, scope expand/collapse, official BIS source links, and audit disclaimer.

### 5. Automated Tests & Quality Assurance
- Test Suite: [`backend/tests/`](file:///c:/Standards-AI/backend/tests/) (`test_db.py`, `test_embedding_qdrant.py`, `test_api.py`).
- 9 passed in 2.41s (re-verified post Pre-Run-2 cleanup).

---

## Next Steps (Handover to Run 2)
- Hybrid retrieval combining dense vector similarity with BM25 / token-level keyword matching.
- Category, department, and standard status filtering.
- Calibrated confidence scoring (High / Medium / Low).
- Evidence-based clause/sentence highlighter explaining exact technical justifications.
