import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert "search_url" in data

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["standards_in_db"] >= 15
    assert data["points_indexed"] >= 15
    assert data["embedding_dimension"] == 384

def test_search_tmt_rebar():
    response = client.post(
        "/api/v1/search",
        json={"query": "12 mm TMT reinforcement bars for RCC construction", "limit": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_matches"] > 0
    assert "audit_disclaimer" in data

    results = data["results"]
    assert len(results) > 0

    # Top match must be IS 1786:2008 (High Strength Deformed Steel Bars)
    top = results[0]
    assert "IS 1786" in top["standard_number"]
    assert "Deformed Steel Bars" in top["title"]
    assert top["similarity_score"] > 0.4
    assert top["source_url"] is not None

def test_search_structural_steel():
    response = client.post(
        "/api/v1/search",
        json={"query": "Hot rolled medium and high tensile structural steel plates for bridge girder fabrication", "limit": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_matches"] > 0
    top = data["results"][0]
    assert "IS 2062" in top["standard_number"] or "IS 800" in top["standard_number"]

def test_search_safety_helmets():
    response = client.post(
        "/api/v1/search",
        json={"query": "Industrial safety helmets for construction workers", "limit": 3}
    )
    assert response.status_code == 200
    data = response.json()
    top = data["results"][0]
    assert "IS 2925" in top["standard_number"]

def test_empty_query():
    response = client.post(
        "/api/v1/search",
        json={"query": "   ", "limit": 5}
    )
    assert response.status_code == 422 or response.status_code == 400
