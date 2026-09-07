# Project State: SIH26108

## Current Status
- **Run 0 (Project Foundation and Environment):** COMPLETED
- **Run 1 (Core Semantic Standards Search MVP):** COMPLETED
- **Run 2 (Improved Ranking, Metadata Filtering, Confidence and Explanations):** NOT STARTED
- **Run 3 to Run 8:** NOT STARTED

---

## Functional Status (Run 1 Completed)
- A working, fully verified vertical slice from authentic BIS seed metadata to browser-based interactive semantic retrieval is operational.
- Users can enter procurement specifications or tender clauses in the React UI and receive real, verified Indian Standards ranked by dense cosine similarity.
- 100% local operation: zero paid API dependencies, zero external cloud requirements.
- 9/9 automated backend tests passing (`pytest backend/tests/ -v`).
- Live end-to-end browser testing verified via automated browser subagent.

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
- 9 passed in 2.55s.

---

## Next Steps (Handover to Run 2)
- Hybrid retrieval combining dense vector similarity with BM25 / token-level keyword matching.
- Category, department, and standard status filtering.
- Calibrated confidence scoring (High / Medium / Low).
- Evidence-based clause/sentence highlighter explaining exact technical justifications.
