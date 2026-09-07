import json
import logging
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.db.database import get_db_cursor, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def seed_database(
    seed_file_path: Path | str | None = None,
    db_path: Path | str | None = None,
    reset: bool = False
) -> int:
    seed_path = Path(seed_file_path or settings.SEED_DATA_PATH)
    if not seed_path.exists():
        raise FileNotFoundError(f"Seed file not found at: {seed_path}")

    init_db(db_path)

    with open(seed_path, "r", encoding="utf-8") as f:
        standards_data: list[dict[str, Any]] = json.load(f)

    logger.info(f"Loaded {len(standards_data)} standards from {seed_path}")

    count = 0
    with get_db_cursor(db_path) as cursor:
        if reset:
            logger.warning("Reset flag is true. Clearing existing standards and relationships...")
            cursor.execute("DELETE FROM standard_relationships;")
            cursor.execute("DELETE FROM standards;")

        for std in standards_data:
            keywords_val = std.get("keywords")
            if isinstance(keywords_val, (list, dict)):
                keywords_val = json.dumps(keywords_val, ensure_ascii=False)

            # Insert or ignore / update
            cursor.execute(
                """
                INSERT INTO standards (
                    standard_number, title, year_of_publication, edition,
                    status, superseded_by, scope, department, category,
                    keywords, source_url, source_evidence_note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(standard_number) DO UPDATE SET
                    title = excluded.title,
                    year_of_publication = excluded.year_of_publication,
                    edition = excluded.edition,
                    status = excluded.status,
                    superseded_by = excluded.superseded_by,
                    scope = excluded.scope,
                    department = excluded.department,
                    category = excluded.category,
                    keywords = excluded.keywords,
                    source_url = excluded.source_url,
                    source_evidence_note = excluded.source_evidence_note,
                    updated_at = CURRENT_TIMESTAMP;
                """,
                (
                    std["standard_number"],
                    std["title"],
                    std.get("year_of_publication"),
                    std.get("edition"),
                    std.get("status", "ACTIVE"),
                    std.get("superseded_by"),
                    std["scope"],
                    std.get("department"),
                    std.get("category"),
                    keywords_val,
                    std.get("source_url"),
                    std.get("source_evidence_note"),
                )
            )
            count += 1

        # Seed key authoritative relationships
        # IS 456 (Concrete) -> IS 1786 (Rebar) and IS 269 (Cement)
        # IS 800 (Steel Design) -> IS 2062 (Structural Steel)
        cursor.execute("SELECT id, standard_number FROM standards")
        mapping = {row["standard_number"]: row["id"] for row in cursor.fetchall()}

        relationships = [
            ("IS 456:2000", "IS 1786:2008", "NORMATIVE_REFERENCE", "Reinforcement steel specification cited in concrete design clause"),
            ("IS 456:2000", "IS 269:2015", "NORMATIVE_REFERENCE", "Cement specification cited in concrete ingredients specification"),
            ("IS 456:2000", "IS 10262:2019", "PRODUCT_COMPANION", "Concrete mix proportioning companion standard"),
            ("IS 800:2007", "IS 2062:2011", "NORMATIVE_REFERENCE", "Structural steel materials reference in limit state steel design"),
            ("IS 1239 (Part 1):2004", "IS 3589:2001", "PRODUCT_COMPANION", "Mild steel piping family companion (small bore vs large bore)"),
        ]

        for src, tgt, rel_type, desc in relationships:
            if src in mapping and tgt in mapping:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO standard_relationships (
                        source_standard_id, target_standard_id, relationship_type, description
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (mapping[src], mapping[tgt], rel_type, desc)
                )

    logger.info(f"Database successfully populated with {count} verified Indian Standards.")
    return count

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Initialize and seed SQLite database with BIS standards.")
    parser.add_argument("--reset", action="store_true", help="Clear existing data before seeding")
    args = parser.parse_args()
    seed_database(reset=args.reset)
