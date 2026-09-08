"""
ComplianceService — deterministic retrieval of verified BIS regulatory compliance & QCO metadata.

This service performs direct SQLite lookups; it never uses an LLM to guess,
hallucinate, or infer regulatory mandates. All records originate from the
curated regulatory compliance dataset (bis_seed_compliance.json) grounded in
official Gazette notifications, QCOs, and BIS compulsory certification schemes.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.db.database import get_compliance_by_number
from app.schemas.compliance import StandardCompliance, CertificationStatus, QCOStatus

logger = logging.getLogger(__name__)


class ComplianceService:
    """
    Provides deterministic retrieval of BIS standard compliance & QCO metadata.

    Design constraints (Run 5A):
    - NO LLM inference or generation of regulatory status.
    - NO automatic assumption that a standard recommendation implies mandatory compliance.
    - Grounded in official QCO orders, Gazette notifications, and BIS Scheme registries.
    """

    def __init__(self, db_path: Path | str | None = None) -> None:
        self._db_path = db_path

    def get_compliance(self, standard_number: str) -> StandardCompliance | None:
        """
        Returns verified compliance metadata for the given BIS standard number.

        Returns None if the standard is not found in the database.
        Returns UNKNOWN/NOT_IDENTIFIED for unverified or non-QCO items without inventing claims.
        """
        try:
            row = get_compliance_by_number(standard_number, db_path=self._db_path)
        except Exception as exc:
            logger.error(
                "Error fetching compliance for %s: %s", standard_number, exc, exc_info=True
            )
            return None

        if row is None:
            return None

        return StandardCompliance.from_db_row(row)

    def get_compliance_dict(self, standard_number: str) -> dict[str, Any] | None:
        """
        Convenience wrapper returning a JSON-serialisable dict.
        """
        comp = self.get_compliance(standard_number)
        return comp.model_dump() if comp else None

    def is_mandatory(self, standard_number: str) -> bool:
        """
        Returns True iff verified evidence confirms mandatory BIS certification
        or an applicable QCO order.
        """
        comp = self.get_compliance(standard_number)
        if comp is None:
            return False
        return (
            comp.certification_status.upper() == CertificationStatus.MANDATORY.value
            or comp.qco_status.upper() == QCOStatus.APPLICABLE.value
        )
