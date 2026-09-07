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

---

## 8. Data Quality Notes (Pre-Run-2 Cleanup)

> Applied after Run 1 completion, before Run 2. No new standards, architecture changes, or Run 2 logic were introduced.

### 8.1 Seed Dataset Scope
Run 1 uses a limited **15-standard seed dataset** covering high-priority public procurement categories. This dataset is intentionally small and curated for demonstration purposes.

Semantic search results indicate **potential relevance** based on cosine similarity against officially stored BIS standard scope text. They do **not** indicate legal applicability, mandatory compliance, or formal procurement authority approval.

### 8.2 Evidence Notes — Claims Removed or Neutralised
The following unsupported regulatory/procurement claims were present in the original `source_evidence_note` fields and have been replaced with neutral, scope-derived descriptions:

| Standard | Original Claim (Removed) | Replacement (Neutral) |
| :--- | :--- | :--- |
| IS 1786:2008 | "widely mandated in CPWD, NHAI, Indian Railways, and state PWD procurement schedules" | "Official BIS standard specification covering high strength deformed steel bars and wires for concrete reinforcement." |
| IS 2062:2011 | "Mandatory standard… covered under Steel and Steel Products QCO" | "Relevant BIS standard covering hot-rolled medium and high tensile structural steel plates, sections, flats, and bars." |
| IS 269:2015 | "under mandatory BIS certification" | "BIS standard specifying chemical and physical requirements for 33, 43, and 53 grades of ordinary Portland cement." |
| IS 694:2010 | "referenced across government building specifications and CPWD electrical schedules" | "BIS standard specifying requirements and tests for PVC insulated electric cables for voltages up to 450/750 V." |
| IS 7098 (Part 1):1988 | "Core standard for… DISCOM and municipal tenders" | "BIS standard covering requirements and tests for XLPE insulated cables for working voltages up to 1100 V." |
| IS 1554 (Part 1):1988 | "extensively used for industrial plants and substation wiring" | "BIS standard covering requirements of PVC insulated heavy duty electric cables for voltages up to 1100 V." |
| IS 4984:2016 | "extensively referenced under Jal Jeevan Mission and urban water supply tenders" | "BIS standard specifying requirements for high density polyethylene (HDPE) pipes for conveyance of water for human consumption." |
| IS 3589:2001 | "Standard for large diameter feeder water mains and transmission pipelines in municipal and regional water supply projects" | "BIS standard covering requirements for seamless or electrically welded steel pipes (168.3 mm to 2540 mm OD) for water, gas, and sewage." |
| IS 2925:1984 | "Mandatory safety helmet standard under BIS certification for construction, mining, and industrial factory procurement" | "BIS standard covering physical, constructional, and performance requirements for industrial safety helmets." |
| IS 15298 (Part 2):2016 | "Enforced under Footwear Quality Control Orders (QCOs)" | "BIS standard specifying basic and additional requirements for safety footwear and protective toecaps." |
| IS 800:2007 | "The national design code for structural steelwork" | "BIS code of practice for general construction and limit state design in structural steel." |
| IS 10262:2019 | "Authoritative guidelines for preparing design mix concrete submitted in contractor quality assurance plans" | "BIS guidelines for proportioning concrete mixes for ordinary, standard, and high strength concrete." |
| IS 1239 (Part 1):2004 | "Standard specification for MS and GI pipes used in plumbing, water distribution, and HVAC services" | "BIS standard specifying requirements for welded and seamless steel tubes and pipes for water, non-hazardous gas, air, and steam." |
| IS 456:2000 | "The national benchmark standard for design and construction of plain and reinforced concrete" | "BIS code of practice for the general structural use and design considerations of plain and reinforced concrete." |
| IS 1077:2020 | "required in CPWD and state government masonry tender schedules" | "BIS standard specifying dimensions, quality, and compressive strength requirements for common burnt clay building bricks." |

### 8.3 Regulatory/QCO Applicability — Intentionally Deferred
Determination of which standards are subject to a Quality Control Order (QCO) or are otherwise legally mandatory is **intentionally deferred to Run 5**. The current system does not store, compute, or display QCO enforcement status. Procurement officers must independently verify regulatory applicability through the official BIS and relevant Ministry notifications.

### 8.4 Source URLs
Source URLs in the seed dataset point to the BIS standards search portal (`standardsbis.bsbedge.com`) using the standard number as a query parameter. These are reference links to the BIS portal search interface and should be treated as starting points for manual verification against the current BIS catalogue, not as guaranteed direct links to the exact standard document page. No URLs were fabricated or altered beyond what was present in the original Run 1 seed data.

### 8.5 UI Wording Changes Applied
- Score badge: `"Semantic Match"` → `"Semantic Relevance"` — to more accurately reflect that the score measures textual similarity against stored scope text, not confirmed applicability.
- Results header badge: `"Grounded in Verified BIS Scope"` → `"Based on Verified BIS Scope"` — cleaner, less assertive phrasing appropriate for a procurement audience.
- Source link label: `"BIS Source Portal"` → `"BIS Reference Link"` — clarifies the link is a search reference, not a direct download.

### 8.6 Configurable Search Limit
The hardcoded `limit: 10` in the search API has been made configurable:
- `DEFAULT_SEARCH_LIMIT = 10` and `MAX_SEARCH_LIMIT = 50` are defined in `app/core/config.py` and overridable via environment variables.
- The `SearchRequest` Pydantic schema reads these values from `settings` instead of hardcoding them.
- The frontend exposes a **Limit** dropdown (Top 5 / Top 10 / Top 15) allowing users to control the number of results returned per query.
- This is a configuration convenience only; no Run 2 ranking or reordering logic has been implemented.
