import logging
from typing import Any
from pathlib import Path

from app.db.database import (
    get_standard_by_number,
    get_standard_relationships_by_number,
    get_standard_relationships_by_id
)

logger = logging.getLogger(__name__)

class RelationshipService:
    """
    Deterministic service for retrieving authoritative BIS standard relationships
    grounded strictly in the SQLite relational database.
    Zero vector similarity inference; zero fabricated relationships.
    """

    def __init__(self, db_path: Path | str | None = None):
        self.db_path = db_path

    def get_related_standards(
        self,
        standard_number: str,
        relationship_type: str | None = None
    ) -> dict[str, Any] | None:
        """
        Retrieves all verified related standards for a given standard number.
        Returns None if the requested standard does not exist in the database.
        """
        std = get_standard_by_number(standard_number, db_path=self.db_path)
        if not std:
            return None

        raw_relationships = get_standard_relationships_by_number(
            standard_number=std["standard_number"],
            relationship_type=relationship_type,
            db_path=self.db_path
        )

        formatted_items = []
        grouped: dict[str, list[dict[str, Any]]] = {}

        for rel in raw_relationships:
            target_data = rel["target"]
            item = {
                "relationship_id": rel["relationship_id"],
                "relationship_type": rel["relationship_type"],
                "description": rel["description"],
                "evidence_text": rel["evidence_text"],
                "target_standard": {
                    "id": target_data.get("id"),
                    "standard_number": target_data["standard_number"],
                    "title": target_data["title"],
                    "year_of_publication": target_data.get("year_of_publication"),
                    "edition": target_data.get("edition"),
                    "status": target_data.get("status", "ACTIVE"),
                    "category": target_data.get("category"),
                    "department": target_data.get("department"),
                    "scope": target_data.get("scope"),
                    "keywords": target_data.get("keywords") or [],
                    "source_url": target_data.get("source_url"),
                    "source_evidence_note": target_data.get("source_evidence_note")
                }
            }
            formatted_items.append(item)
            
            rel_type = rel["relationship_type"]
            if rel_type not in grouped:
                grouped[rel_type] = []
            grouped[rel_type].append(item)

        return {
            "standard_number": std["standard_number"],
            "title": std["title"],
            "total_relationships": len(formatted_items),
            "relationships": formatted_items,
            "grouped_by_type": grouped
        }

_default_relationship_service: RelationshipService | None = None

def get_relationship_service(db_path: Path | str | None = None) -> RelationshipService:
    global _default_relationship_service
    if db_path is not None:
        return RelationshipService(db_path=db_path)
    if _default_relationship_service is None:
        _default_relationship_service = RelationshipService()
    return _default_relationship_service
