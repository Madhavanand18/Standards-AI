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
    evidence_source_title: str | None = None
    evidence_source_url: str | None = None
    evidence_source_type: str | None = None
    notes: str | None = None
    last_verified: str | None = None

    @classmethod
    def from_db_row(cls, row: dict[str, Any]) -> "StandardCompliance":
        """Construct from SQLite query dictionary."""
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
            evidence_source_title=row.get("evidence_source_title"),
            evidence_source_url=row.get("evidence_source_url"),
            evidence_source_type=row.get("evidence_source_type"),
            notes=row.get("notes"),
            last_verified=row.get("last_verified"),
        )
