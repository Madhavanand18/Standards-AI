from pydantic import BaseModel, Field
from typing import Any

class RelatedStandardDetail(BaseModel):
    id: int | None = None
    standard_number: str
    title: str
    year_of_publication: int | None = None
    edition: str | None = None
    status: str = "ACTIVE"
    category: str | None = None
    department: str | None = None
    scope: str | None = None
    keywords: list[str] = Field(default_factory=list)
    source_url: str | None = None
    source_evidence_note: str | None = None

class StandardRelationshipItem(BaseModel):
    relationship_id: int
    relationship_type: str = Field(
        ...,
        description="Type of relationship (e.g. normative_reference, test_method, terminology, related_product, design_code, safety)"
    )
    description: str | None = None
    evidence_text: str | None = Field(
        None,
        description="Clause or standard scope evidence text grounding this relationship"
    )
    target_standard: RelatedStandardDetail

class StandardRelationshipsResponse(BaseModel):
    standard_number: str
    title: str
    total_relationships: int
    relationships: list[StandardRelationshipItem]
    grouped_by_type: dict[str, list[StandardRelationshipItem]] = Field(
        default_factory=dict,
        description="Relationships organized by relationship type (normative_reference, design_code, etc.)"
    )
