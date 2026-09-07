# Implementation Roadmap: SIH26108

> **CORE PRINCIPLES OF THE RUN ROADMAP**  
> 1. **Zero-Broken-State Invariant:** Each run must leave the project in an independently working, fully verifiable state.  
> 2. **No Forward Dependencies:** Never make a future run a prerequisite for the current run to operate.  
> 3. **Incremental Enhancement:** Each run introduces a specific, testable layer of functionality on top of the established foundation.

---

## Run Overview

| Run | Milestone | Focus Area | Deliverable Status |
| :--- | :--- | :--- | :--- |
| **RUN 0** | **Foundation & Environment** | Workspace setup, architectural contracts, directory structure, memory files | IN PROGRESS |
| **RUN 1** | **Core Semantic Standards Search MVP** | Real BIS metadata, local embeddings, Qdrant index, semantic search API, minimal UI | NOT STARTED |
| **RUN 2** | **Ranking, Filtering & Explanations** | Hybrid ranking, metadata filtering, confidence scores, evidence-based citations | NOT STARTED |
| **RUN 3** | **Related & Normative Standards** | Relationship graph (SQLite), companion test methods, safety standards | NOT STARTED |
| **RUN 4** | **Revisions, Amendments & Outdated Detection** | Version tracking, superseded standard alerts, amendment history | NOT STARTED |
| **RUN 5** | **QCO & Mandatory Certifications** | Quality Control Order database, mandatory compliance badges, ministry orders | NOT STARTED |
| **RUN 6** | **Tender & PDF Document Analysis** | Unstructured tender clause ingestion, batch spec parsing, requirement extraction | NOT STARTED |
| **RUN 7** | **Multilingual Input Processing** | Multilingual input support (Hindi + Indian languages), cross-lingual retrieval | NOT STARTED |
| **RUN 8** | **Testing, Deployment & Final Presentation** | End-to-end integration tests, containerization, demo scripts, SIH presentation | NOT STARTED |

---

## Detailed Run Specifications

### RUN 0: Project Foundation and Environment
- **Objective:** Establish the permanent engineering foundation, directory scaffolding, Git initialization, and persistent memory files.
- **Key Deliverables:**
  - Project memory files: `PROJECT_CONTEXT.md`, `PROJECT_STATE.md`, `ARCHITECTURE.md`, `DEVELOPMENT_RULES.md`, `RUN_ROADMAP.md`.
  - Minimal root `README.md` and `.gitignore`.
  - Directory skeleton for backend (`backend/`), frontend (`frontend/`), and data storage (`data/`).
  - Verification of runtime tools (Python 3.13+, Node.js 22+, Git).
- **Working State Guarantee:** Repository is clean, structured, and ready for immediate Run 1 kickoff with zero architectural ambiguities.

---

### RUN 1: Core Semantic Standards Search MVP
- **Objective:** Build a working vertical slice from real BIS metadata ingestion to interactive semantic search in a basic UI.
- **Key Deliverables:**
  - Seed dataset of authoritative BIS standards (curated high-impact procurement domains: structural steel, cement, electrical cables, PPE, pipes).
  - SQLite database schema initialization and seed script (`data/db/standards.db`).
  - Local multilingual embedding generation module.
  - Local Qdrant collection setup with payload metadata.
  - FastAPI `/api/v1/search` endpoint performing semantic similarity search.
  - Minimal React + Vite UI: query box, search trigger, and list of matched standards with scores.
- **Working State Guarantee:** A user can type a procurement item description (e.g., "high tensile structural steel plates for bridge fabrication") and receive real, verified IS standard recommendations (e.g., IS 2062) in the browser.

---

### RUN 2: Improved Ranking, Metadata Filtering, Confidence and Explanations
- **Objective:** Enhance search precision through hybrid scoring (semantic vector + BM25/keyword), field filters, confidence calculation, and evidence explanations.
- **Key Deliverables:**
  - Hybrid retrieval combining dense vector similarity with keyword/code matching.
  - Category, department, and status filtering.
  - Calibrated confidence scoring (High / Medium / Low match indicator).
  - Evidence generator extracting relevant scope sentences justifying why the standard matches the input.
- **Working State Guarantee:** Recommendations display distinct confidence ratings and highlighted text excerpts explaining relevance.

---

### RUN 3: Related, Allied, Normative, Test, and Safety Standards
- **Objective:** Surface the ecosystem of companion standards required alongside the primary product standard.
- **Key Deliverables:**
  - SQLite `standard_relationships` table population.
  - Automatic resolution of normative references (e.g., specifying IS 2062 surfaces IS 1599 for bend tests, IS 1608 for tensile testing).
  - UI display grouping results into Primary Product Standards, Companion Test Methods, and Safety Codes.
- **Working State Guarantee:** Searching for a product standard automatically presents the mandatory test protocols and companion standards required in a tender specification.

---

### RUN 4: Versions, Amendments, and Outdated-Reference Detection
- **Objective:** Flag obsolete or withdrawn standards cited in legacy tender documents and suggest the valid current edition.
- **Key Deliverables:**
  - Version and supersession graph in SQLite.
  - Detection pipeline for outdated citations (e.g., identifying when an old specification cites an obsolete revision year).
  - Redirection logic to current active standard with amendment details.
- **Working State Guarantee:** Entering an obsolete standard number or text citing old standards triggers an explicit "Outdated / Superseded" warning with the replacement standard.

---

### RUN 5: QCO and Certification Information
- **Objective:** Integrate Quality Control Orders (QCOs) issued by Indian ministries under the BIS Act.
- **Key Deliverables:**
  - QCO mapping table linking mandatory certification orders to corresponding IS numbers.
  - Visual badges for "Mandatory BIS Certification / QCO Enforced".
  - Details on enforcing ministry, notification date, and legal compliance notes.
- **Working State Guarantee:** Items under mandatory QCOs prominently display legal compliance requirements to safeguard buyers against non-compliant procurement.

---

### RUN 6: Tender/PDF Analysis
- **Objective:** Allow procurement officials to upload tender PDF documents or paste long multi-clause technical schedules.
- **Key Deliverables:**
  - Text extraction pipeline for PDF and text tender documents.
  - Chunking and clause isolation for technical specifications.
  - Batch recommendation covering multi-item tenders.
- **Working State Guarantee:** Uploading a sample tender document produces a comprehensive standards compliance matrix across all detected line items.

---

### RUN 7: Multilingual Input
- **Objective:** Support procurement queries and tender specifications in Indian languages (e.g., Hindi).
- **Key Deliverables:**
  - Cross-lingual semantic retrieval using the multilingual embedding model.
  - Query translation / normalizer for vernacular technical terms.
  - UI localization toggles.
- **Working State Guarantee:** Specifications entered in Hindi yield accurate Indian Standards with explanations in the selected language.

---

### RUN 8: Testing, Deployment and Final SIH Presentation
- **Objective:** Comprehensive testing, production packaging, presentation scripts, and deployment demonstration.
- **Key Deliverables:**
  - Automated test suite (unit tests for backend pipeline, retrieval precision benchmarks).
  - Standalone startup scripts / Docker setup for quick judging demonstration.
  - Pitch deck alignment, sample tender test cases, and presentation walkthrough.
- **Working State Guarantee:** The entire platform can be booted with a single command and demonstrated reliably during live SIH evaluation.
