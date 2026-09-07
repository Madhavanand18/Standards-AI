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

def test_qdrant_retrieval():
    svc = get_embedding_service()
    store = get_vector_store()

    # Query for TMT rebar
    query_vec = svc.embed_text("12 mm TMT reinforcement bars for RCC construction")
    results = store.search(query_vector=query_vec, limit=3)

    assert len(results) > 0
    top_result = results[0]
    top_standard = top_result["payload"]["standard_number"]
    assert "IS 1786" in top_standard
    assert top_result["score"] > 0.4
