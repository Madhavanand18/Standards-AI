# System Architecture: SIH26108

> **LOCKED ARCHITECTURAL SPECIFICATION**  
> This architecture is finalized for SIH26108. Future AI agents, contributors, and team members must strictly adhere to the technology stack and pipeline defined herein. Do not substitute core components without explicit user authorization.

---

## 1. Technology Stack & Component Responsibilities

| Layer | Technology | Role & Constraints |
| :--- | :--- | :--- |
| **Frontend** | **React + Vite** | High-performance single page application (SPA). Fast load times, clean procurement input form, structured display of recommended standards, citations, and confidence badges. Avoid heavy UI libraries. |
| **Backend** | **Python + FastAPI** | High-concurrency asynchronous API server. Houses pipeline orchestrator, embedding service, database repositories, and query endpoints. Fully typed with Pydantic. |
| **Relational Database** | **SQLite** | Local, zero-configuration relational database. Stores canonical BIS standards metadata, revision history, normative relationships, and QCO status. |
| **Vector Database** | **Qdrant** | High-performance vector database (local storage / embedded mode for MVP). Indexing dense embeddings of standard titles, scopes, and technical keywords with payload-based filtering. |
| **Embedding Layer** | **Local Multilingual Embedding Model** | Free, open-weights embedding model (e.g., `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` or `BAAI/bge-m3`). Runs locally without external paid API dependencies. |
| **LLM Layer** | **Constrained Utility LLM** | Used **strictly** for: (1) extracting structured procurement parameters from noisy tender text, and (2) drafting natural-language justifications citing retrieved standard scopes. **NEVER** used as the source of truth for standard numbers or applicability. |
| **Knowledge Base** | **Structured BIS Metadata** | Authoritative dataset of Indian Standards (IS number, year, edition, status, scope, product categories, amendments, normative references). |

---

## 2. Core End-to-End Pipeline

```
┌───────────────────────────────────────────────────────────┐
│              1. User Procurement Input                    │
│   (Item description, technical spec, or tender clause)   │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│            2. Requirement Extraction (LLM/Rule)           │
│   (Product type, material, grade, operational parameters) │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│            3. Local Multilingual Embedding               │
│   (Encodes extracted requirements into dense vector)      │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│            4. Qdrant Vector Retrieval                     │
│   (Similarity search across standard scopes & titles)     │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│       5. Relational Verification & Ranking (SQLite)       │
│   - Check standard status (active/superseded)             │
│   - Traverse companion test/safety/normative standards    │
│   - Check QCO mandatory certification status              │
│   - Apply hybrid keyword/attribute matching               │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│         6. Recommendation & Confidence Scoring            │
│   (Ranked list of primary + normative standards)          │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│               7. Verification & Explanation               │
│   (Clause/scope evidence-backed explanation for buyers)   │
└───────────────────────────────────────────────────────────┘
```

---

## 3. Data Storage & Schema Design

### 3.1 SQLite Relational Schema (Canonical Metadata)
- **`standards`**:
  - `id` (INTEGER PRIMARY KEY)
  - `standard_number` (TEXT UNIQUE NOT NULL) — e.g., "IS 2062"
  - `title` (TEXT NOT NULL) — e.g., "Hot Rolled Medium and High Tensile Structural Steel"
  - `year_of_publication` (INTEGER NOT NULL)
  - `edition` (TEXT)
  - `status` (TEXT NOT NULL) — "ACTIVE", "WITHDRAWN", "SUPERSEDED"
  - `superseded_by` (TEXT NULL) — references newer standard number
  - `scope` (TEXT NOT NULL) — official BIS scope summary
  - `department` (TEXT) — e.g., "Civil Engineering", "Metallurgical"
  - `created_at`, `updated_at`
- **`standard_relationships`**:
  - `id` (INTEGER PRIMARY KEY)
  - `source_standard_id` (INTEGER REFERENCES standards(id))
  - `target_standard_id` (INTEGER REFERENCES standards(id))
  - `relationship_type` (TEXT NOT NULL) — "NORMATIVE_REFERENCE", "TEST_METHOD", "PRODUCT_COMPANION", "SUPERSEDED_BY"
- **`quality_control_orders`** (QCOs):
  - `id` (INTEGER PRIMARY KEY)
  - `standard_id` (INTEGER REFERENCES standards(id))
  - `order_name` (TEXT NOT NULL) — e.g., "Steel and Steel Products (Quality Control) Order"
  - `ministry` (TEXT) — e.g., "Ministry of Steel"
  - `date_enforced` (TEXT)
  - `is_mandatory` (BOOLEAN DEFAULT 1)

### 3.2 Qdrant Vector Collection Design
- **Collection Name:** `bis_standards`
- **Vector Size:** Model-dependent (e.g., 384 for MiniLM-L12-v2 or 1024 for BGE-M3)
- **Distance Metric:** Cosine similarity
- **Payload Schema:**
  - `standard_number`: string (e.g., "IS 2062:2011")
  - `title`: string
  - `status`: string ("ACTIVE", "SUPERSEDED")
  - `department`: string
  - `category_tags`: array of strings
  - `scope_snippet`: string (for fast UI rendering)

---

## 4. Architectural Boundaries & Invariants

1. **Deterministic Grounding:** No standard can be suggested to the user unless it exists in SQLite and Qdrant. Hallucination of standard codes is strictly prevented by foreign-key lookups.
2. **Local-First Embeddings:** Vector generation operates locally without incurring API bills, latency variations, or external cloud outages during SIH judging.
3. **Auditability:** Every recommendation payload returned to the frontend contains:
   - Match confidence score (0.0 to 1.0)
   - Scope citation (exact excerpt from official BIS record)
   - Validity indicator (Active vs Outdated)
   - Mandatory QCO warning (if applicable)
4. **Decoupled Frontend-Backend:** The frontend communicates with the backend exclusively via typed REST APIs (`/api/v1/...`).
