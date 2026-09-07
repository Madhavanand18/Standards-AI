# Development Rules & Architectural Invariants

> **MANDATORY INSTRUCTIONS FOR ALL DEVELOPERS AND AI AGENTS**  
> These rules are inviolable. Before writing, modifying, or refactoring code in this repository, you must review and comply with every rule in this document.

---

## 1. Architectural Stability
1. **Do not randomly change the architecture.** The architectural blueprint defined in `ARCHITECTURE.md` is locked.
2. **Do not replace FastAPI.** Python + FastAPI is the dedicated backend framework.
3. **Do not replace React/Vite.** The frontend must remain lightweight React built with Vite.
4. **Do not replace Qdrant.** Qdrant is the designated vector database for dense similarity retrieval. Do not replace it with Chroma, Pinecone, Milvus, Weaviate, or FAISS unless explicitly instructed by the user.
5. **Do not replace SQLite for MVP metadata.** SQLite is the single source of truth for structured relational standards metadata and relationships in the MVP. Do not substitute PostgreSQL, MySQL, or MongoDB.
6. **Do not add microservices.** Keep the application a clean, modular monolith (FastAPI backend + React frontend).
7. **Do not add Kubernetes or complex orchestration.** The project must be runnable on a developer laptop or single VM without enterprise cluster overhead.
8. **Do not introduce unnecessary frameworks.** Avoid heavy ORMs, complex state machines, or unnecessary dependencies that complicate setup.

---

## 2. Standards Data Integrity & Correctness
1. **Never use fake or synthetic BIS standards in the final application.** All standards surfaced to users must correspond to genuine Indian Standards issued by the Bureau of Indian Standards.
2. **Do not claim a standard is applicable without evidence from the knowledge base.** Every recommendation must cite verified scope text or clause data stored in the database.
3. **The LLM is NOT the source of truth for standards.** Never allow an LLM to generate standard numbers from its parametric memory. Candidate standards must be retrieved from Qdrant and validated in SQLite.
4. **Prioritize correctness and reliability over visual polish.** A recommendation engine for public procurement must be legally and technically accurate above all else.

---

## 3. Scope and Feature Discipline
1. **Do not add authentication unless explicitly requested.** Do not waste time or complexity on user logins, JWTs, OAuth, or role-based access control unless the user mandates it.
2. **Do not build unnecessary UI features.** Focus exclusively on what is required to input procurement specifications and inspect recommended standards with clarity.
3. **Keep the project modular so future runs can extend it.** Code must be structured into clean, decoupled layers (models, repositories, services, API routes).
4. **Never delete working functionality merely to simplify implementation.** Preserve existing, verified features when advancing across runs.

---

## 4. Run Progression Discipline
1. **Follow the roadmap strictly.** Work only on the designated Run as defined in `RUN_ROADMAP.md`.
2. **Each run must leave the project in a working state.** Never leave broken builds, crashing servers, or incomplete migrations.
3. **Never make a future run a dependency for the current run to function.** Run N must be completely operational even if Run N+1 is not yet started.
4. **Do not proceed to the next run automatically.** Complete the verification checklist, update `PROJECT_STATE.md`, and await user approval before moving to subsequent runs.
