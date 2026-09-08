import pytest
from app.services.embedding import get_embedding_service
from app.services.vector_store import get_vector_store

def test_embedding_service():
    svc = get_embedding_service()
    assert svc.dimension == 384

    text = "Mild steel ERW pipes for water supply"
    vec = svc.embed_text(text)
    assert isinstance(vec, list)
    assert len(vec) == 384
    assert all(isinstance(x, float) for x in vec)

    batch_vecs = svc.embed_batch([text, "Personal protective safety helmets"])
    assert len(batch_vecs) == 2
    assert len(batch_vecs[0]) == 384
    assert len(batch_vecs[1]) == 384

from app.services.vector_store import QdrantVectorStore

def test_qdrant_retrieval():
    svc = get_embedding_service()
    # Use isolated in-memory vector store to prevent disk lock conflicts during test runs
    store = QdrantVectorStore(storage_path=":memory:")
    store.ensure_collection(dimension=svc.dimension)

    records = [
        {
            "id": 1,
            "standard_number": "IS 1786:2008",
            "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement",
            "category": "Reinforcement Steel / Construction",
            "scope": "Covers requirements of deformed steel bars and wires for use as reinforcement in concrete in strength grades Fe 415, Fe 500.",
            "keywords": ["TMT bars", "reinforcement steel", "RCC", "Fe 500"]
        },
        {
            "id": 2,
            "standard_number": "IS 2925:1984",
            "title": "Specification for Industrial Safety Helmets",
            "category": "Personal Protective Equipment",
            "scope": "Covers requirements for industrial safety helmets for head protection against falling objects.",
            "keywords": ["safety helmets", "PPE", "head protection"]
        }
    ]

    texts = [f"{r['standard_number']} | {r['title']} | {r['scope']}" for r in records]
    vectors = svc.embed_batch(texts)
    store.upsert_records(records=records, vectors=vectors)

    # Query for TMT rebar
    query_vec = svc.embed_text("12 mm TMT reinforcement bars for RCC construction")
    results = store.search(query_vector=query_vec, limit=2)

    assert len(results) > 0
    top_result = results[0]
    top_standard = top_result["payload"]["standard_number"]
    assert "IS 1786" in top_standard
    assert top_result["score"] > 0.4
