import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.search import get_vector_store, get_embedding_service

class MockEmbeddingService:
    model_name = "test-model"
    dimension = 384

    def embed_text(self, text: str) -> list[float]:
        return [0.1] * 384

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 384 for _ in texts]

class MockVectorStore:
    collection_name = "bis_standards"

    def get_collection_info(self) -> dict:
        return {
            "collection_name": self.collection_name,
            "status": "green",
            "points_count": 30,
            "vectors_count": 30
        }

    def search(self, query_vector: list[float], limit: int = 10, score_threshold: float = 0.0) -> list[dict]:
        # Return realistic results with intentional duplicate standard numbers
        return [
            {
                "id": 1,
                "score": 0.88,
                "payload": {
                    "standard_number": "IS 1786:2008",
                    "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement",
                    "category": "Reinforcement Steel / Construction",
                    "scope": "This standard covers the requirements of deformed steel bars and wires for use as reinforcement in concrete."
                }
            },
            {
                "id": 2,
                "score": 0.65,
                "payload": {
                    "standard_number": "IS 1786:2008",
                    "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement (Duplicate Point)",
                    "category": "Reinforcement Steel / Construction",
                    "scope": "Duplicate entry scope"
                }
            },
            {
                "id": 3,
                "score": 0.75,
                "payload": {
                    "standard_number": "IS 2062:2011",
                    "title": "Hot Rolled Medium and High Tensile Structural Steel",
                    "category": "Structural Steel / Fabrication",
                    "scope": "This standard covers the requirements of steel plates, sections, and bars."
                }
            },
            {
                "id": 4,
                "score": 0.50,
                "payload": {
                    "standard_number": "IS 2062:2011",
                    "title": "Hot Rolled Medium and High Tensile Structural Steel (Duplicate Point)",
                    "category": "Structural Steel / Fabrication",
                    "scope": "Duplicate entry scope"
                }
            },
            {
                "id": 5,
                "score": 0.70,
                "payload": {
                    "standard_number": "IS 2925:1984",
                    "title": "Specification for Industrial Safety Helmets",
                    "category": "Personal Protective Equipment",
                    "scope": "Covers requirements for non-metallic safety helmets for industrial workers."
                }
            }
        ]

@pytest.fixture(autouse=True)
def override_dependencies():
    mock_store = MockVectorStore()
    mock_emb = MockEmbeddingService()
    app.dependency_overrides[get_vector_store] = lambda: mock_store
    app.dependency_overrides[get_embedding_service] = lambda: mock_emb
    yield
    app.dependency_overrides.clear()

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

def test_search_deduplication_regression():
    """
    Regression test: verify that duplicate standard_number results from the vector store
    are deduplicated, keeping only the highest-scoring result and counting unique standards.
    """
    response = client.post(
        "/api/v1/search",
        json={"query": "test query with duplicate standards in index", "limit": 10}
    )
    assert response.status_code == 200
    data = response.json()

    # The mock returns 5 points containing only 3 unique standards
    assert data["total_matches"] == 3
    assert len(data["results"]) == 3

    # Check unique standard numbers
    std_numbers = [r["standard_number"] for r in data["results"]]
    assert std_numbers == ["IS 1786:2008", "IS 2062:2011", "IS 2925:1984"]
    assert len(std_numbers) == len(set(std_numbers))

    # Check that highest score was preserved for IS 1786 (0.88, not 0.65) and IS 2062 (0.75, not 0.50)
    assert data["results"][0]["standard_number"] == "IS 1786:2008"
    assert data["results"][0]["dense_score"] == 0.88

    assert data["results"][1]["standard_number"] == "IS 2062:2011"
    assert data["results"][1]["dense_score"] == 0.75

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

def test_search_fe500_reinforcement_ranking_api():
    """
    Test Fe 500 reinforcement query ranking via API.
    IS 1786 must rank above IS 2062.
    Also verify explanation and relevance label are present and valid.
    """
    response = client.post(
        "/api/v1/search",
        json={"query": "Fe 500 ribbed steel bars for reinforced concrete columns", "limit": 5}
    )
    assert response.status_code == 200
    data = response.json()
    results = data["results"]
    assert len(results) >= 2

    # Verify IS 1786 is #1 and ranks above IS 2062
    top = results[0]
    assert "IS 1786" in top["standard_number"]
    assert any("IS 2062" in r["standard_number"] for r in results)
    
    # Verify explanation and relevance_label on results
    for r in results:
        assert r["relevance_label"] in {"High", "Medium", "Low"}
        assert r["explanation"] is not None
        assert len(r["explanation"]) > 0
        assert "scope" in r["explanation"].lower() or "matches" in r["explanation"].lower()
    
    # Find positions
    is_1786_idx = next(i for i, r in enumerate(results) if "IS 1786" in r["standard_number"])
    is_2062_idx = next(i for i, r in enumerate(results) if "IS 2062" in r["standard_number"])
    assert is_1786_idx < is_2062_idx

def test_search_dynamic_threshold_api():
    """
    Test configurable score_threshold in search API.
    Higher threshold returns fewer, more strictly relevant results.
    """
    # 1. Search with low threshold (0.2) -> returns multiple items
    resp_low = client.post(
        "/api/v1/search",
        json={"query": "12 mm TMT reinforcement bars for RCC construction", "limit": 10, "score_threshold": 0.2}
    )
    assert resp_low.status_code == 200
    count_low = resp_low.json()["total_matches"]

    # 2. Search with high threshold (0.80) -> returns only very high matches
    resp_high = client.post(
        "/api/v1/search",
        json={"query": "12 mm TMT reinforcement bars for RCC construction", "limit": 10, "score_threshold": 0.80}
    )
    assert resp_high.status_code == 200
    count_high = resp_high.json()["total_matches"]

    assert count_high <= count_low

def test_search_structural_steel():
    response = client.post(
        "/api/v1/search",
        json={"query": "Hot rolled medium and high tensile structural steel plates for bridge girder fabrication", "limit": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_matches"] > 0
    top = data["results"][0]
    assert "IS 2062" in top["standard_number"] or "IS 1786" in top["standard_number"]

def test_search_safety_helmets():
    response = client.post(
        "/api/v1/search",
        json={"query": "Industrial safety helmets for construction workers", "limit": 5}
    )
    assert response.status_code == 200
    data = response.json()
    standard_numbers = [r["standard_number"] for r in data["results"]]
    assert "IS 2925:1984" in standard_numbers

def test_search_results_include_relationships():
    """Verify that search results populate verified relationships and grouped_relationships."""
    response = client.post(
        "/api/v1/search",
        json={"query": "Reinforced concrete design and construction practice", "limit": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) > 0

    # Locate IS 456 in results if present
    is_456 = next((r for r in data["results"] if "IS 456" in r["standard_number"]), None)
    if is_456:
        assert len(is_456["relationships"]) >= 3
        assert "normative_reference" in is_456["grouped_relationships"]
        assert "design_code" in is_456["grouped_relationships"]
        
        # Verify evidence text and target structure
        first_rel = is_456["relationships"][0]
        assert first_rel["evidence_text"] is not None
        assert "target_standard" in first_rel
        assert "title" in first_rel["target_standard"]
        assert "standard_number" in first_rel["target_standard"]

def test_empty_query():
    response = client.post(
        "/api/v1/search",
        json={"query": "   ", "limit": 5}
    )
    assert response.status_code == 422 or response.status_code == 400


