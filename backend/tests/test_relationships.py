import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import (
    get_standard_by_number,
    get_standard_relationships_by_number,
    get_standard_relationships_by_id,
    get_db_cursor
)
from app.services.relationships import RelationshipService, get_relationship_service

client = TestClient(app)

def test_relationship_schema_and_seeding():
    """Verify that the standard_relationships table contains authoritative seed records."""
    with get_db_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as cnt FROM standard_relationships")
        count = cursor.fetchone()["cnt"]
        assert count >= 19, f"Expected at least 19 relationships in DB, got {count}"

        # Verify a specific relationship integrity
        cursor.execute("""
            SELECT r.relationship_type, r.description, s1.standard_number as src, s2.standard_number as tgt
            FROM standard_relationships r
            JOIN standards s1 ON r.source_standard_id = s1.id
            JOIN standards s2 ON r.target_standard_id = s2.id
            WHERE s1.standard_number = 'IS 456:2000' AND s2.standard_number = 'IS 1786:2008'
        """)
        row = cursor.fetchone()
        assert row is not None
        assert row["relationship_type"] == "normative_reference"
        assert "Clause 5.6.1" in row["description"]


def test_db_get_standard_relationships_by_number():
    """Verify database helper get_standard_relationships_by_number."""
    rels = get_standard_relationships_by_number("IS 456:2000")
    assert len(rels) >= 3
    
    target_numbers = [r["target"]["standard_number"] for r in rels]
    assert "IS 1786:2008" in target_numbers
    assert "IS 269:2015" in target_numbers
    assert "IS 10262:2019" in target_numbers

    # Verify evidence text is populated
    for r in rels:
        assert r["evidence_text"] is not None
        assert len(r["evidence_text"]) > 10
        assert r["relationship_type"] in ["normative_reference", "design_code", "related_product", "safety", "test_method", "terminology"]


def test_db_filter_by_relationship_type():
    """Verify filtering database relationships by type."""
    normative_rels = get_standard_relationships_by_number("IS 456:2000", relationship_type="normative_reference")
    assert len(normative_rels) == 2
    for r in normative_rels:
        assert r["relationship_type"] == "normative_reference"

    design_rels = get_standard_relationships_by_number("IS 456:2000", relationship_type="design_code")
    assert len(design_rels) == 1
    assert design_rels[0]["target"]["standard_number"] == "IS 10262:2019"


def test_relationship_service_get_related_standards():
    """Verify RelationshipService layer retrieval and grouping."""
    service = get_relationship_service()
    data = service.get_related_standards("IS 800:2007")
    
    assert data is not None
    assert data["standard_number"] == "IS 800:2007"
    assert data["total_relationships"] == 2
    assert "normative_reference" in data["grouped_by_type"]
    
    targets = [r["target_standard"]["standard_number"] for r in data["relationships"]]
    assert "IS 2062:2011" in targets
    assert "IS 1239 (Part 1):2004" in targets

    # Check non-existent standard returns None
    assert service.get_related_standards("IS 99999:2099") is None


def test_api_get_standard_relationships_success():
    """Test API GET /api/v1/standards/{standard_number}/relationships endpoint."""
    response = client.get("/api/v1/standards/IS 456:2000/relationships")
    assert response.status_code == 200
    
    data = response.json()
    assert data["standard_number"] == "IS 456:2000"
    assert data["total_relationships"] >= 3
    assert "relationships" in data
    assert "grouped_by_type" in data
    assert "normative_reference" in data["grouped_by_type"]

    # Verify first item structure
    first_rel = data["relationships"][0]
    assert "relationship_type" in first_rel
    assert "evidence_text" in first_rel
    assert "target_standard" in first_rel
    assert "title" in first_rel["target_standard"]
    assert "status" in first_rel["target_standard"]


def test_api_get_standard_relationships_prefix_match():
    """Test API resolves normalized prefix like 'IS 456' to 'IS 456:2000'."""
    response = client.get("/api/v1/standards/IS 456/relationships")
    assert response.status_code == 200
    data = response.json()
    assert data["standard_number"] == "IS 456:2000"


def test_api_get_standard_relationships_type_filter():
    """Test API filtering by relationship_type."""
    response = client.get("/api/v1/standards/IS 456:2000/relationships?relationship_type=design_code")
    assert response.status_code == 200
    data = response.json()
    assert data["total_relationships"] == 1
    assert data["relationships"][0]["target_standard"]["standard_number"] == "IS 10262:2019"


def test_api_query_relationships_endpoint():
    """Test API GET /api/v1/relationships?standard_number=... endpoint."""
    response = client.get("/api/v1/relationships?standard_number=IS 2925:1984")
    assert response.status_code == 200
    data = response.json()
    assert data["standard_number"] == "IS 2925:1984"
    assert data["total_relationships"] == 1
    assert data["relationships"][0]["relationship_type"] == "safety"
    assert data["relationships"][0]["target_standard"]["standard_number"] == "IS 15298 (Part 2):2016"
    assert "safety footwear" in data["relationships"][0]["evidence_text"].lower()


def test_api_relationships_not_found():
    """Test 404 for unknown standard."""
    response = client.get("/api/v1/standards/IS 99999:2099/relationships")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
