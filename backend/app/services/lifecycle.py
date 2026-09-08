"""
LifecycleService — deterministic retrieval of verified BIS standard lifecycle metadata.

This service performs direct SQLite lookups; it does not use an LLM to infer,
guess, or generate any lifecycle attribute.  All data originates from the
curated BIS seed lifecycle file (bis_seed_lifecycle.json) which itself is
grounded in the official BIS catalog/portal.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.db.database import get_lifecycle_by_number
from app.schemas.lifecycle import StandardLifecycle

logger = logging.getLogger(__name__)


class LifecycleService:
    """
    Provides deterministic retrieval of BIS standard lifecycle metadata.

    Design constraints (Run 4A):
    - NO LLM inference or generation.
    - NO site scraping at request time.
    - Data must trace to bis_seed_lifecycle.json (BIS-sourced evidence).
    """

    def __init__(self, db_path: Path | str | None = None) -> None:
        self._db_path = db_path

    def get_lifecycle(self, standard_number: str) -> StandardLifecycle | None:
        """
        Returns verified lifecycle metadata for the given BIS standard number.

        Returns None if the standard is not found in the database.
        Never fabricates missing fields — uses null/UNKNOWN for unverified data.
        """
        try:
            row = get_lifecycle_by_number(standard_number, db_path=self._db_path)
        except Exception as exc:
            logger.error(
                "Error fetching lifecycle for %s: %s", standard_number, exc, exc_info=True
            )
            return None

        if row is None:
            return None

        return StandardLifecycle.from_db_row(row)

    def get_lifecycle_dict(self, standard_number: str) -> dict[str, Any] | None:
        """
        Convenience wrapper that returns a JSON-serialisable dict.
        """
        lc = self.get_lifecycle(standard_number)
        return lc.model_dump() if lc else None

    def is_current(self, standard_number: str) -> bool | None:
        """
        Returns True iff the lifecycle_status is 'ACTIVE', False if it is
        any superseded/withdrawn status, and None if the standard is unknown.
        """
        lc = self.get_lifecycle(standard_number)
        if lc is None:
            return None
        return lc.lifecycle_status.upper() == "ACTIVE"
