# Run 1 Milestone Report: Core Semantic Standards Search MVP

> **Milestone:** RUN 1 — Core Semantic Standards Search MVP  
> **Status:** COMPLETED & VERIFIED  
> **Date:** September 7, 2026  
> **Repository:** SIH26108 Standards-AI

---

## 1. What Was Implemented

In Run 1, we constructed an end-to-end, zero-cost, locally executable semantic search MVP for Indian Standards without external cloud or paid API dependencies:

1. **Authoritative BIS Seed Dataset:** Curated 15 genuine Indian Standards across major public procurement sectors (rebar, structural steel, concrete, cement, piping, electrical cables, PPE, bricks).
2. **SQLite Relational Metadata Store:** Implemented schema and tables (`standards`, `standard_relationships`), indexes, and safe idempotent seeding script.
3. **Local Multilingual Embedding Pipeline:** Designed a clean abstract interface (`BaseEmbeddingService`) implemented via `FastEmbedService` running ONNX Runtime locally on CPU.
4. **Local Qdrant Vector Database:** Configured embedded disk-based Qdrant vector database (`bis_standards` collection) storing 384-dimensional dense vectors alongside rich metadata payloads.
5. **Idempotent Ingestion & Indexing Pipeline:** Automated batch reading from SQLite, semantic string formatting, embedding generation, and Qdrant upsertion.
6. **FastAPI Endpoints:** Built `/api/v1/health` and `/api/v1/search` with typed Pydantic models, CORS middleware, and audit disclaimers.
7. **React + Vite Frontend UI:** Created an intuitive search UI using vanilla CSS with quick example chips, score badges, scope expansion, and official BIS portal links.
8. **Automated & End-to-End Tests:** Built 9 automated unit/integration tests with `pytest` and verified the full user flow using automated browser subagents.

---

## 2. Seed Standards Included

All 15 standards represent authentic, current Bureau of Indian Standards specifications with verified scopes:

| Standard Number | Title | Category | Department |
| :--- | :--- | :--- | :--- |
| **IS 1786:2008** | High Strength Deformed Steel Bars and Wires for Concrete Reinforcement — Specification | Reinforcement Steel / Construction | Civil Engineering |
| **IS 2062:2011** | Hot Rolled Medium and High Tensile Structural Steel — Specification | Structural Steel | Metallurgical Engineering |
| **IS 456:2000** | Plain and Reinforced Concrete — Code of Practice | Civil Engineering / Concrete | Civil Engineering |
| **IS 269:2015** | Ordinary Portland Cement — Specification | Cement & Concrete Materials | Civil Engineering |
| **IS 694:2010** | PVC Insulated Unsheathed and Sheathed Cables/Cords for Voltages up to 450/750 V | Electrical Cables | Electrotechnical |
| **IS 7098 (Part 1):1988** | XLPE Insulated Thermoplastic Sheathed Cables for Voltages up to 1100 V | Electrical Cables | Electrotechnical |
| **IS 1554 (Part 1):1988** | PVC Insulated (Heavy Duty) Electric Cables for Voltages up to 1100 V | Electrical Cables | Electrotechnical |
| **IS 1239 (Part 1):2004** | Steel Tubes, Tubulars and Other Wrought Steel Fittings: Part 1 Steel Tubes | Steel Pipes & Fittings | Mechanical Engineering |
| **IS 4984:2016** | High Density Polyethylene (HDPE) Pipes for Water Supply — Specification | Plastic Piping Systems | Civil Engineering / Piping |
| **IS 3589:2001** | Seamless or Electrically Welded Steel Pipes for Water, Gas and Sewage | Steel Pipes & Fittings | Mechanical Engineering |
| **IS 2925:1984** | Specification for Industrial Safety Helmets | Personal Protective Equipment | Chemical / Safety |
| **IS 15298 (Part 2):2016** | Personal Protective Equipment - Part 2: Safety Footwear | Personal Protective Equipment | Chemical / Footwear |
| **IS 800:2007** | General Construction in Steel — Code of Practice | Structural Steel / Design | Civil Engineering |
| **IS 10262:2019** | Concrete Mix Proportioning — Guidelines | Civil Engineering / Concrete | Civil Engineering |
| **IS 1077:2020** | Common Burnt Clay Building Bricks — Specification | Building Materials | Civil Engineering |

---

## 3. Embedding Model

- **Model Name:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Runtime:** FastEmbed ONNX Runtime (CPU execution)
- **Vector Dimension:** 384 dimensions
- **Cost / Keys:** Free, 0 API keys, runs locally on developer laptop.
- **Multilingual Support:** Supports 50+ languages including English and Indian languages (Hindi, etc.).

---

## 4. Qdrant Configuration

- **Storage Mode:** Local embedded disk storage (`data/qdrant_storage/`) with zero external Docker daemon requirement. Optionally configurable via `QDRANT_URL`.
- **Collection Name:** `bis_standards`
- **Vector Dimension:** 384
- **Distance Metric:** Cosine Similarity
- **Payload Schema:**
  - `db_id`: SQLite primary key
  - `standard_number`: e.g. "IS 1786:2008"
  - `title`: Standard title
  - `category`: Classification domain
  - `department`: BIS technical division
  - `status`: "ACTIVE"
  - `year_of_publication`: Integer
  - `edition`: String
  - `source_url`: Link to official BIS portal
  - `source_evidence_note`: Institutional evidence note
  - `scope_snippet`: Short excerpt for UI cards
  - `scope`: Full official BIS scope text
  - `keywords`: Array of search keywords

---

## 5. API Endpoints

### `GET /api/v1/health`
- Verifies operational status, counts SQLite standards, inspects Qdrant collection status, and returns embedding model info.

### `POST /api/v1/search`
- Request body: `{"query": string, "limit": integer}`
- Generates query embedding vector, performs Qdrant cosine similarity search, and formats ranked results alongside official BIS metadata.
- Appends anti-hallucination compliance disclaimer.

---

## 6. Tests Performed

### 6.1 Automated Backend Pytest Suite
Ran `pytest backend/tests/ -v` (9 passed in 2.55s):
1. `test_root_endpoint`: Verifies root metadata.
2. `test_health_endpoint`: Verifies healthy status, 15 database records, 15 Qdrant points.
3. `test_search_tmt_rebar`: Asserts `"12 mm TMT reinforcement bars for RCC construction"` ranks `IS 1786:2008` as #1 with >0.6 score.
4. `test_search_structural_steel`: Asserts structural steel query ranks `IS 2062:2011` and `IS 800:2007`.
5. `test_search_safety_helmets`: Asserts PPE helmet query ranks `IS 2925:1984`.
6. `test_empty_query`: Tests validation handling for empty queries.
7. `test_init_db_and_seeding`: Tests isolated temporary SQLite DB initialization, schema integrity, and relationships.
8. `test_embedding_service`: Tests vector dimension (384) and batch generation.
9. `test_qdrant_retrieval`: Tests vector search directly against Qdrant index.

### 6.2 Browser Subagent End-to-End Verification
- Tested live UI at `http://127.0.0.1:5173/`
- Verified header status indicators: "Database: 15 standards · Vectors: 15 indexed"
- Executed search for `"12 mm TMT reinforcement bars for RCC construction"` -> `IS 1786:2008` loaded with 61% match, expanded full scope, verified source link.
- Executed search for `"Industrial safety helmets for construction workers"` -> `IS 2925:1984` loaded with 78% match.
- Screen recording captured and saved to artifacts.

---

## 7. Known Limitations & Run 2 Boundaries

1. **Vector-Only Retrieval:** Currently relies purely on dense semantic vector similarity; exact alphanumeric standard numbers (e.g. typing "IS 2062") or specific grade codes are better matched when combined with BM25 / token matching (scheduled for Run 2).
2. **No Field Filtering:** Searching cannot yet be filtered by Department or Category (scheduled for Run 2).
3. **Discrete Confidence Calibration:** Scores are raw cosine similarities rather than calibrated High/Medium/Low confidence bands (scheduled for Run 2).
4. **Scope Excerpt Highlighting:** The UI currently displays the scope snippet rather than highlighting the specific matched sentence (scheduled for Run 2).
