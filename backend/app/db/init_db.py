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
    seed_rel_path: Path | str | None = None,
    seed_lifecycle_path: Path | str | None = None,
    seed_compliance_path: Path | str | None = None,
    db_path: Path | str | None = None,
    reset: bool = False
) -> int:
    seed_path = Path(seed_file_path or settings.SEED_DATA_PATH)
    if not seed_path.exists():
        raise FileNotFoundError(f"Seed file not found at: {seed_path}")

    rel_path = Path(seed_rel_path or settings.SEED_RELATIONSHIPS_PATH)
    lc_path = Path(seed_lifecycle_path or settings.SEED_LIFECYCLE_PATH)
    comp_path = Path(seed_compliance_path or settings.SEED_COMPLIANCE_PATH)

    init_db(db_path)

    with open(seed_path, "r", encoding="utf-8") as f:
        standards_data: list[dict[str, Any]] = json.load(f)

    logger.info(f"Loaded {len(standards_data)} standards from {seed_path}")

    count = 0
    with get_db_cursor(db_path) as cursor:
        if reset:
            logger.warning("Reset flag is true. Clearing existing data...")
            cursor.execute("DELETE FROM standard_compliance;")
            cursor.execute("DELETE FROM standard_amendments;")
            cursor.execute("DELETE FROM standard_lifecycle;")
            cursor.execute("DELETE FROM standard_relationships;")
            cursor.execute("DELETE FROM standards;")

        for std in standards_data:
            keywords_val = std.get("keywords")
            if isinstance(keywords_val, (list, dict)):
                keywords_val = json.dumps(keywords_val, ensure_ascii=False)

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

        # Build mapping of standard_number to ID
        cursor.execute("SELECT id, standard_number FROM standards")
        mapping = {row["standard_number"]: row["id"] for row in cursor.fetchall()}

        # Load and seed lifecycle metadata
        lc_count = 0
        amd_count = 0
        if lc_path.exists():
            with open(lc_path, "r", encoding="utf-8") as lf:
                lifecycle_data: list[dict[str, Any]] = json.load(lf)

            # Cleanly sync lifecycle tables
            cursor.execute("DELETE FROM standard_amendments;")
            cursor.execute("DELETE FROM standard_lifecycle;")

            for lc in lifecycle_data:
                std_num = lc["standard_number"]
                if std_num not in mapping:
                    logger.warning(f"Lifecycle entry for unknown standard: {std_num} — skipped")
                    continue

                std_id = mapping[std_num]
                cursor.execute(
                    """
                    INSERT INTO standard_lifecycle (
                        standard_id, lifecycle_status, reaffirmed_year, reviewed_year,
                        amendment_count, supersedes, superseded_by, source_url,
                        verification_date, verification_note
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(standard_id) DO UPDATE SET
                        lifecycle_status = excluded.lifecycle_status,
                        reaffirmed_year = excluded.reaffirmed_year,
                        reviewed_year = excluded.reviewed_year,
                        amendment_count = excluded.amendment_count,
                        supersedes = excluded.supersedes,
                        superseded_by = excluded.superseded_by,
                        source_url = excluded.source_url,
                        verification_date = excluded.verification_date,
                        verification_note = excluded.verification_note,
                        updated_at = CURRENT_TIMESTAMP;
                    """,
                    (
                        std_id,
                        lc.get("lifecycle_status", "UNKNOWN"),
                        lc.get("reaffirmed_year"),
                        lc.get("reviewed_year"),
                        lc.get("amendment_count", 0),
                        lc.get("supersedes"),
                        lc.get("superseded_by"),
                        lc.get("source_url"),
                        lc.get("verification_date"),
                        lc.get("verification_note"),
                    )
                )
                lc_count += 1

                # Seed amendments
                for amd in lc.get("amendments", []):
                    cursor.execute(
                        """
                        INSERT INTO standard_amendments (
                            standard_id, amendment_number, year, description,
                            source_url, verification_date
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(standard_id, amendment_number) DO UPDATE SET
                            year = excluded.year,
                            description = excluded.description,
                            source_url = excluded.source_url,
                            verification_date = excluded.verification_date;
                        """,
                        (
                            std_id,
                            amd["amendment_number"],
                            amd.get("year"),
                            amd.get("description"),
                            amd.get("source_url"),
                            amd.get("verification_date"),
                        )
                    )
                    amd_count += 1

        # Load and seed compliance metadata
        comp_count = 0
        if comp_path.exists():
            with open(comp_path, "r", encoding="utf-8") as cf:
                compliance_data: list[dict[str, Any]] = json.load(cf)

            cursor.execute("DELETE FROM standard_compliance;")

            for comp in compliance_data:
                std_num = comp["standard_number"]
                if std_num not in mapping:
                    logger.warning(f"Compliance entry for unknown standard: {std_num} — skipped")
                    continue

                std_id = mapping[std_num]
                cursor.execute(
                    """
                    INSERT INTO standard_compliance (
                        standard_id, certification_status, certification_scheme, qco_status,
                        qco_reference, qco_title, issuing_authority, enforcement_date,
                        evidence_source_title, evidence_source_url, evidence_source_type,
                        notes, last_verified
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(standard_id) DO UPDATE SET
                        certification_status = excluded.certification_status,
                        certification_scheme = excluded.certification_scheme,
                        qco_status = excluded.qco_status,
                        qco_reference = excluded.qco_reference,
                        qco_title = excluded.qco_title,
                        issuing_authority = excluded.issuing_authority,
                        enforcement_date = excluded.enforcement_date,
                        evidence_source_title = excluded.evidence_source_title,
                        evidence_source_url = excluded.evidence_source_url,
                        evidence_source_type = excluded.evidence_source_type,
                        notes = excluded.notes,
                        last_verified = excluded.last_verified,
                        updated_at = CURRENT_TIMESTAMP;
                    """,
                    (
                        std_id,
                        comp.get("certification_status", "UNKNOWN"),
                        comp.get("certification_scheme"),
                        comp.get("qco_status", "UNKNOWN"),
                        comp.get("qco_reference"),
                        comp.get("qco_title"),
                        comp.get("issuing_authority"),
                        comp.get("enforcement_date"),
                        comp.get("evidence_source_title"),
                        comp.get("evidence_source_url"),
                        comp.get("evidence_source_type"),
                        comp.get("notes"),
                        comp.get("last_verified"),
                    )
                )
                comp_count += 1

        # Load relationships from curated JSON file if available
        relationships_to_seed = []
        if rel_path.exists():
            with open(rel_path, "r", encoding="utf-8") as rf:
                rel_data: list[dict[str, Any]] = json.load(rf)
                for r in rel_data:
                    relationships_to_seed.append((
                        r["source_standard_number"],
                        r["target_standard_number"],
                        r["relationship_type"].lower(),
                        r.get("evidence_text") or r.get("description", "")
                    ))
        else:
            # Authoritative default fallback relationships
            relationships_to_seed = [
                ("IS 456:2000", "IS 1786:2008", "normative_reference", "Clause 5.6.1 of IS 456 specifies high strength deformed steel bars conforming to IS 1786 for reinforced concrete construction."),
                ("IS 456:2000", "IS 269:2015", "normative_reference", "Clause 5.1(a) of IS 456 specifies 33, 43, and 53 grade Ordinary Portland Cement conforming to IS 269 as standard cementitious binder."),
                ("IS 456:2000", "IS 10262:2019", "design_code", "Clause 9.1.1 of IS 456 references IS 10262 for standard guidelines and calculations on concrete mix proportioning."),
                ("IS 800:2007", "IS 2062:2011", "normative_reference", "Section 2 and Table 1 of IS 800 specify hot-rolled medium and high tensile structural steel conforming to IS 2062 for structural steelwork design."),
                ("IS 800:2007", "IS 1239 (Part 1):2004", "normative_reference", "Section 2 of IS 800 lists steel tubes conforming to IS 1239 (Part 1) as approved tubular structural hollow sections."),
            ]

        # Cleanly synchronize relationship table to prevent case duplicate entries
        cursor.execute("DELETE FROM standard_relationships;")

        rel_count = 0
        for src, tgt, rel_type, desc in relationships_to_seed:
            if src in mapping and tgt in mapping:
                cursor.execute(
                    """
                    INSERT INTO standard_relationships (
                        source_standard_id, target_standard_id, relationship_type, description
                    ) VALUES (?, ?, ?, ?)
                    ON CONFLICT(source_standard_id, target_standard_id, relationship_type) DO UPDATE SET
                        description = excluded.description
                    """,
                    (mapping[src], mapping[tgt], rel_type.lower(), desc)
                )
                rel_count += 1

    logger.info(
        f"Database successfully populated with {count} standards, "
        f"{lc_count} lifecycle records, {amd_count} amendments, "
        f"{comp_count} compliance records, and {rel_count} relationships."
    )
    return count


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Initialize and seed SQLite database with BIS standards.")
    parser.add_argument("--reset", action="store_true", help="Clear existing data before seeding")
    args = parser.parse_args()
    seed_database(reset=args.reset)


