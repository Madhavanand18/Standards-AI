# Project Context: SIH26108

## 1. Problem Statement Summary
- **Problem Statement ID:** SIH26108
- **Title:** AI-Powered Recommendation Engine for Identifying Applicable Indian Standards for Procurement Specifications
- **Theme:** Smart Automation / Public Procurement / Standardization (Bureau of Indian Standards - BIS)
- **Background:** Public procurement in India (conducted through the Government e-Marketplace [GeM], Central Public Procurement Portal [CPPP], Indian Railways, Defence, CPWD, and public sector undertakings) involves massive expenditure on goods, works, and services. To ensure quality, safety, interoperability, and durability, procurement specifications must reference applicable Bureau of Indian Standards (BIS) specifications.
- **The Core Problem:** 
  1. With over 22,000+ active Indian Standards, multiple technical committees, periodic amendments, revisions, and supersessions, procurement officers often specify outdated, incorrect, or incomplete standards.
  2. Many items fall under mandatory Quality Control Orders (QCOs) issued by various ministries under the BIS Act, making compliance legally obligatory. Missed QCO references can lead to tender cancellations or procurement of non-compliant goods.
  3. Specifications often miss crucial companion standards (normative references, sampling methods, and safety/acceptance testing standards).
  4. Manual search through standard catalogs is slow, keyword-sensitive, and error-prone for non-specialist procurement officers.

---

## 2. Project Objective
To develop a reliable, AI-powered recommendation system that takes technical procurement requirements or draft tender specifications as input and automatically:
1. Identifies all applicable primary Indian Standards (IS).
2. Surfaces mandatory Quality Control Orders (QCOs) and regulatory compliance requirements.
3. Maps normative companion standards (test methods, sampling protocols, related specifications).
4. Verifies standard validity (active, revised, withdrawn, or superseded).
5. Explains the exact rationale and technical evidence connecting the procurement specification to each recommended standard.

---

## 3. Intended Users
- **Procurement Officers & Indenting Officers:** Government buyers and PSU tender drafting officials writing technical schedules on GeM or department portals.
- **Tender Scrutiny & Evaluation Committees:** Officials evaluating technical bids against national quality norms.
- **Compliance & Quality Assurance Auditors:** Third-party inspection agencies and vigilance officers verifying adherence to standards and QCO mandates.
- **Vendors, Suppliers & Bidders:** Manufacturers and suppliers seeking to identify the exact IS compliance requirements needed to qualify for government tenders.

---

## 4. Core Functionality
- **Requirement Extraction:** Extracts key technical attributes (item category, material grade, dimensions, performance requirements, operating environment) from unstructured procurement text.
- **Semantic & Keyword Retrieval:** Performs high-recall semantic vector search over standard titles, scopes, and keywords using a local multilingual embedding model coupled with Qdrant.
- **Relational Verification & Filtering:** Resolves candidate standards against an authoritative SQLite metadata database (validating status, edition, amendments, and normative linkages).
- **Rule-Based & Evidence-Backed Ranking:** Re-ranks candidate standards using domain heuristics (exact product classification match, QCO applicability, active validity).
- **Explainable Output:** Generates clear, audit-ready explanations indicating *why* each standard is applicable based strictly on verified standard scopes and requirements.

---

## 5. What This System Is NOT
- **NOT an Unconstrained Hallucinatory Chatbot:** The LLM is NEVER used as the source of truth for standard numbers, titles, or statuses. All standards must exist in the authoritative BIS database.
- **NOT a Document Reseller or Pirate:** The system does not redistribute proprietary full-text BIS standard documents. It operates on publicly available metadata, titles, scopes, amendments, tables of contents, and cross-references.
- **NOT a Black-Box Classifier:** Every recommendation includes verifiable citations, scope excerpts, and rule-based justifications for procurement auditing.
- **NOT an Autonomous Authority:** The engine is an intelligent assistant for human procurement officers; final procurement decisions remain with the designated procurement authority.

---

## 6. Current MVP Scope (Run 0 to Run 1 Foundation)
- Focused on structured BIS metadata ingestion for high-priority procurement categories.
- Local multilingual embedding generation.
- Qdrant-powered vector similarity search on standard scopes and technical descriptions.
- SQLite-backed relational metadata storage for status, edition, and category mapping.
- Python FastAPI backend serving structured recommendation endpoints.
- Lightweight React + Vite frontend for entering specifications and reviewing recommended standards.
