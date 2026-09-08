from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class CertificationStatus(str, Enum):
    MANDATORY = "MANDATORY"
    VOLUNTARY = "VOLUNTARY"
    NOT_IDENTIFIED = "NOT_IDENTIFIED"
    UNKNOWN = "UNKNOWN"


class QCOStatus(str, Enum):
    APPLICABLE = "APPLICABLE"
    UPCOMING = "UPCOMING"
    NOT_IDENTIFIED = "NOT_IDENTIFIED"
    UNKNOWN = "UNKNOWN"


class ComplianceEvent(BaseModel):
    """
    Represents a specific regulatory or version transition milestone in a standard's compliance history.
    """
    id: int | None = None
    event_date: str | None = None
    event_type: str  # e.g., INITIAL_QCO, AMENDMENT, EXTENSION, REVISED_STANDARD, IMPLEMENTATION_GUIDELINE
    title: str
    description: str | None = None
    reference_doc: str | None = None
    source_url: str | None = None


class StandardCompliance(BaseModel):
    """
    Verified regulatory compliance and Quality Control Order (QCO) metadata for a BIS standard.
    All data is grounded in authoritative BIS / Government gazette evidence.
    """
    standard_id: int | None = None
    standard_number: str
    certification_status: str = CertificationStatus.UNKNOWN.value
    certification_scheme: str | None = None
    qco_status: str = QCOStatus.UNKNOWN.value
    qco_reference: str | None = None
    qco_title: str | None = None
    issuing_authority: str | None = None
    enforcement_date: str | None = None
    referenced_standard_edition: str | None = None
    latest_standard_version: str | None = None
    qco_clause_standard_applicability: str | None = None
    evidence_source_title: str | None = None
    evidence_source_url: str | None = None
    evidence_source_type: str | None = None
    notes: str | None = None
    last_verified: str | None = None
    events: list[ComplianceEvent] = Field(default_factory=list)

    @classmethod
    def from_db_row(cls, row: dict[str, Any]) -> "StandardCompliance":
        """Construct from SQLite query dictionary."""
        events_raw = row.get("events") or []
        events = [
            ComplianceEvent(
                id=e.get("id"),
                event_date=e.get("event_date"),
                event_type=e.get("event_type", "GENERAL"),
                title=e.get("title", ""),
                description=e.get("description"),
                reference_doc=e.get("reference_doc"),
                source_url=e.get("source_url"),
            )
            for e in events_raw
        ]

        return cls(
            standard_id=row.get("standard_id"),
            standard_number=row["standard_number"],
            certification_status=row.get("certification_status", CertificationStatus.UNKNOWN.value),
            certification_scheme=row.get("certification_scheme"),
            qco_status=row.get("qco_status", QCOStatus.UNKNOWN.value),
            qco_reference=row.get("qco_reference"),
            qco_title=row.get("qco_title"),
            issuing_authority=row.get("issuing_authority"),
            enforcement_date=row.get("enforcement_date"),
            referenced_standard_edition=row.get("referenced_standard_edition"),
            latest_standard_version=row.get("latest_standard_version"),
            qco_clause_standard_applicability=row.get("qco_clause_standard_applicability"),
            evidence_source_title=row.get("evidence_source_title"),
            evidence_source_url=row.get("evidence_source_url"),
            evidence_source_type=row.get("evidence_source_type"),
            notes=row.get("notes"),
            last_verified=row.get("last_verified"),
            events=events,
        )
