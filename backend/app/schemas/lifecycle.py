from __future__ import annotations

from pydantic import BaseModel
from typing import Any


class StandardAmendment(BaseModel):
    """Represents a single verified amendment to a BIS standard."""
    amendment_number: int
    year: int | None = None
    description: str | None = None
    source_url: str | None = None
    verification_date: str | None = None


class StandardLifecycle(BaseModel):
    """
    Verified lifecycle and version metadata for a BIS standard.
    All fields are grounded in evidence from the BIS catalog or BIS portal.
    """
    standard_id: int | None = None
    standard_number: str
    title: str
    year_of_publication: int | None = None
    edition: str | None = None
    lifecycle_status: str = "UNKNOWN"
    reaffirmed_year: int | None = None
    reviewed_year: int | None = None
    amendment_count: int = 0
    supersedes: str | None = None
    superseded_by: str | None = None
    source_url: str | None = None
    verification_date: str | None = None
    verification_note: str | None = None
    amendments: list[StandardAmendment] = []

    @classmethod
    def from_db_row(cls, row: dict[str, Any]) -> "StandardLifecycle":
        """Construct from the dict returned by get_lifecycle_by_number."""
        amendments = [
            StandardAmendment(
                amendment_number=a["amendment_number"],
                year=a.get("year"),
                description=a.get("description"),
                source_url=a.get("source_url"),
                verification_date=a.get("verification_date"),
            )
            for a in (row.get("amendments") or [])
        ]
        return cls(
            standard_id=row.get("standard_id"),
            standard_number=row["standard_number"],
            title=row["title"],
            year_of_publication=row.get("year_of_publication"),
            edition=row.get("edition"),
            lifecycle_status=row.get("lifecycle_status", "UNKNOWN"),
            reaffirmed_year=row.get("reaffirmed_year"),
            reviewed_year=row.get("reviewed_year"),
            amendment_count=row.get("amendment_count", 0),
            supersedes=row.get("supersedes"),
            superseded_by=row.get("superseded_by"),
            source_url=row.get("source_url"),
            verification_date=row.get("verification_date"),
            verification_note=row.get("verification_note"),
            amendments=amendments,
        )
