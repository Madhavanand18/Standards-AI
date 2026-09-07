# SIH26108: AI-Powered Recommendation Engine for Applicable Indian Standards

> **Smart India Hackathon 2026**  
> Problem Statement: **SIH26108**  
> Domain: Public Procurement / Bureau of Indian Standards (BIS) Quality Compliance

---

## 1. Overview
This project builds an intelligent recommendation and compliance engine for public procurement officials, tender committees, and bidders. Given an unstructured technical procurement specification or draft tender clause, the system identifies the exact applicable Indian Standards (IS), surfaces mandatory Quality Control Orders (QCOs), maps companion test/safety methods, and provides audit-ready technical justifications.

---

## 2. Repository Structure

```
Standards-AI/
├── .gitignore               # Git ignore configuration
├── README.md                # Project overview and directory guide (this file)
├── PROJECT_CONTEXT.md       # Problem statement, users, non-goals, and core scope
├── PROJECT_STATE.md         # Current execution state and run status tracking
├── ARCHITECTURE.md          # Locked tech stack, data pipeline, and database schemas
├── DEVELOPMENT_RULES.md     # Inviolable development constraints and guidelines
├── RUN_ROADMAP.md           # 9-step incremental roadmap (Run 0 to Run 8)
├── backend/                 # Python + FastAPI backend service
│   ├── app/                 # Application code (APIs, services, schemas, models)
│   └── tests/               # Backend automated tests
├── frontend/                # React + Vite frontend application
├── data/                    # Data storage and pipelines
│   ├── raw/                 # Raw BIS standards metadata and source catalogs
│   ├── processed/           # Processed and normalized standard records
│   └── db/                  # SQLite database files (standards.db)
└── docs/                    # Architecture diagrams, specifications, and presentation assets
```

---

## 3. Technology Stack (Locked)

- **Frontend:** React + Vite
- **Backend:** Python + FastAPI
- **Database:** SQLite (Relational metadata and relationships)
- **Vector Database:** Qdrant (Local / embedded storage for dense vector similarity)
- **Embedding Layer:** Free/local multilingual sentence embedding model
- **LLM Role:** Constrained to parameter extraction and explanation drafting (never the source of truth for standards)

---

## 4. Key Project Memory Documents

Before contributing or modifying code, all developers and AI agents must consult:
1. [`PROJECT_CONTEXT.md`](file:///c:/Standards-AI/PROJECT_CONTEXT.md): Background, target users, and non-goals.
2. [`ARCHITECTURE.md`](file:///c:/Standards-AI/ARCHITECTURE.md): Technical architecture and pipeline contracts.
3. [`DEVELOPMENT_RULES.md`](file:///c:/Standards-AI/DEVELOPMENT_RULES.md): Inviolable rules and constraints.
4. [`RUN_ROADMAP.md`](file:///c:/Standards-AI/RUN_ROADMAP.md): Step-by-step deliverable specifications.
5. [`PROJECT_STATE.md`](file:///c:/Standards-AI/PROJECT_STATE.md): Current active status and completed runs.

---

## 5. Current Project Status
- **Current Run:** RUN 0 (Project Foundation and Environment) — COMPLETED
- **Next Run:** RUN 1 (Core Semantic Standards Search MVP)
