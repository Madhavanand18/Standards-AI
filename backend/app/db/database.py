import sqlite3
import json
from pathlib import Path
from typing import Any, Generator
from contextlib import contextmanager

from app.core.config import settings

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS standards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    standard_number TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    year_of_publication INTEGER,
    edition TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    superseded_by TEXT,
    scope TEXT NOT NULL,
    department TEXT,
    category TEXT,
    keywords TEXT,
    source_url TEXT,
    source_evidence_note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS standard_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_standard_id INTEGER NOT NULL REFERENCES standards(id) ON DELETE CASCADE,
    target_standard_id INTEGER NOT NULL REFERENCES standards(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_standard_id, target_standard_id, relationship_type)
);

CREATE TABLE IF NOT EXISTS standard_lifecycle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    standard_id INTEGER NOT NULL UNIQUE REFERENCES standards(id) ON DELETE CASCADE,
    lifecycle_status TEXT NOT NULL DEFAULT 'UNKNOWN',
    reaffirmed_year INTEGER,
    reviewed_year INTEGER,
    amendment_count INTEGER DEFAULT 0,
    supersedes TEXT,
    superseded_by TEXT,
    source_url TEXT,
    verification_date TEXT,
    verification_note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS standard_amendments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    standard_id INTEGER NOT NULL REFERENCES standards(id) ON DELETE CASCADE,
    amendment_number INTEGER NOT NULL,
    year INTEGER,
    description TEXT,
    source_url TEXT,
    verification_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(standard_id, amendment_number)
);

CREATE TABLE IF NOT EXISTS standard_compliance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    standard_id INTEGER NOT NULL UNIQUE REFERENCES standards(id) ON DELETE CASCADE,
    certification_status TEXT NOT NULL DEFAULT 'UNKNOWN',
    certification_scheme TEXT,
    qco_status TEXT NOT NULL DEFAULT 'UNKNOWN',
    qco_reference TEXT,
    qco_title TEXT,
    issuing_authority TEXT,
    enforcement_date TEXT,
    evidence_source_title TEXT,
    evidence_source_url TEXT,
    evidence_source_type TEXT,
    notes TEXT,
    last_verified TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_standards_number ON standards(standard_number);
CREATE INDEX IF NOT EXISTS idx_standards_category ON standards(category);
CREATE INDEX IF NOT EXISTS idx_standards_status ON standards(status);
CREATE INDEX IF NOT EXISTS idx_rel_source ON standard_relationships(source_standard_id);
CREATE INDEX IF NOT EXISTS idx_rel_target ON standard_relationships(target_standard_id);
CREATE INDEX IF NOT EXISTS idx_lifecycle_standard ON standard_lifecycle(standard_id);
CREATE INDEX IF NOT EXISTS idx_amendments_standard ON standard_amendments(standard_id);
CREATE INDEX IF NOT EXISTS idx_compliance_standard ON standard_compliance(standard_id);
CREATE INDEX IF NOT EXISTS idx_compliance_cert_status ON standard_compliance(certification_status);
CREATE INDEX IF NOT EXISTS idx_compliance_qco_status ON standard_compliance(qco_status);
"""

def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path or settings.SQLITE_DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextmanager
def get_db_cursor(db_path: Path | str | None = None) -> Generator[sqlite3.Cursor, None, None]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db(db_path: Path | str | None = None) -> None:
    """Creates tables and indexes if they do not exist."""
    with get_db_cursor(db_path) as cursor:
        cursor.executescript(CREATE_TABLES_SQL)

def get_all_standards(db_path: Path | str | None = None) -> list[dict[str, Any]]:
    """Retrieves all active standards from SQLite."""
    with get_db_cursor(db_path) as cursor:
        cursor.execute("SELECT * FROM standards ORDER BY id ASC")
        rows = cursor.fetchall()
        results = []
        for r in rows:
            item = dict(r)
            if item.get("keywords") and isinstance(item["keywords"], str):
                try:
                    item["keywords"] = json.loads(item["keywords"])
                except Exception:
                    item["keywords"] = [k.strip() for k in item["keywords"].split(",") if k.strip()]
            results.append(item)
        return results

def get_standard_by_number(standard_number: str, db_path: Path | str | None = None) -> dict[str, Any] | None:
    """Retrieves standard by its standard_number (exact match or normalized match)."""
    with get_db_cursor(db_path) as cursor:
        cursor.execute("SELECT * FROM standards WHERE standard_number = ?", (standard_number.strip(),))
        row = cursor.fetchone()
        if not row:
            # Fallback to search if query is like 'IS 456' matching 'IS 456:2000'
            cursor.execute("SELECT * FROM standards WHERE standard_number LIKE ? LIMIT 1", (f"{standard_number.strip()}%",))
            row = cursor.fetchone()
        if not row:
            return None
        item = dict(row)
        if item.get("keywords") and isinstance(item["keywords"], str):
            try:
                item["keywords"] = json.loads(item["keywords"])
            except Exception:
                item["keywords"] = [k.strip() for k in item["keywords"].split(",") if k.strip()]
        return item

def get_standard_relationships_by_number(
    standard_number: str,
    relationship_type: str | None = None,
    db_path: Path | str | None = None
) -> list[dict[str, Any]]:
    """
    Retrieves all related standards for a given standard_number (outgoing links).
    """
    std = get_standard_by_number(standard_number, db_path=db_path)
    if not std:
        return []
    return get_standard_relationships_by_id(std["id"], relationship_type=relationship_type, db_path=db_path)

def get_standard_relationships_by_id(
    standard_id: int,
    relationship_type: str | None = None,
    db_path: Path | str | None = None
) -> list[dict[str, Any]]:
    """
    Retrieves all related standards for a given standard_id.
    """
    query = """
    SELECT 
        r.id AS relationship_id,
        r.relationship_type,
        r.description,
        r.created_at AS relationship_created_at,
        src.id AS source_id,
        src.standard_number AS source_standard_number,
        src.title AS source_title,
        tgt.id AS target_id,
        tgt.standard_number AS target_standard_number,
        tgt.title AS target_title,
        tgt.year_of_publication AS target_year_of_publication,
        tgt.edition AS target_edition,
        tgt.status AS target_status,
        tgt.scope AS target_scope,
        tgt.department AS target_department,
        tgt.category AS target_category,
        tgt.keywords AS target_keywords,
        tgt.source_url AS target_source_url,
        tgt.source_evidence_note AS target_source_evidence_note
    FROM standard_relationships r
    JOIN standards src ON r.source_standard_id = src.id
    JOIN standards tgt ON r.target_standard_id = tgt.id
    WHERE r.source_standard_id = ?
    """
    params: list[Any] = [standard_id]
    if relationship_type:
        query += " AND LOWER(r.relationship_type) = LOWER(?)"
        params.append(relationship_type.strip())
    
    query += " ORDER BY r.relationship_type ASC, tgt.standard_number ASC"

    with get_db_cursor(db_path) as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        results = []
        for r in rows:
            row_dict = dict(r)
            keywords = row_dict.get("target_keywords")
            if keywords and isinstance(keywords, str):
                try:
                    keywords = json.loads(keywords)
                except Exception:
                    keywords = [k.strip() for k in keywords.split(",") if k.strip()]
            
            item = {
                "relationship_id": row_dict["relationship_id"],
                "relationship_type": row_dict["relationship_type"].lower(),
                "description": row_dict["description"],
                "evidence_text": row_dict["description"],
                "source": {
                    "id": row_dict["source_id"],
                    "standard_number": row_dict["source_standard_number"],
                    "title": row_dict["source_title"]
                },
                "target": {
                    "id": row_dict["target_id"],
                    "standard_number": row_dict["target_standard_number"],
                    "title": row_dict["target_title"],
                    "year_of_publication": row_dict["target_year_of_publication"],
                    "edition": row_dict["target_edition"],
                    "status": row_dict["target_status"],
                    "scope": row_dict["target_scope"],
                    "department": row_dict["target_department"],
                    "category": row_dict["target_category"],
                    "keywords": keywords or [],
                    "source_url": row_dict["target_source_url"],
                    "source_evidence_note": row_dict["target_source_evidence_note"]
                }
            }
            results.append(item)
        return results


def get_lifecycle_by_standard_id(
    standard_id: int,
    db_path: Path | str | None = None
) -> dict[str, Any] | None:
    """
    Retrieves lifecycle metadata for a given standard id.
    Returns None if no lifecycle record exists.
    """
    with get_db_cursor(db_path) as cursor:
        cursor.execute(
            "SELECT * FROM standard_lifecycle WHERE standard_id = ?",
            (standard_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return dict(row)


def get_amendments_by_standard_id(
    standard_id: int,
    db_path: Path | str | None = None
) -> list[dict[str, Any]]:
    """
    Retrieves all amendments for a given standard_id, ordered by amendment number.
    """
    with get_db_cursor(db_path) as cursor:
        cursor.execute(
            "SELECT * FROM standard_amendments WHERE standard_id = ? ORDER BY amendment_number ASC",
            (standard_id,)
        )
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def get_lifecycle_by_number(
    standard_number: str,
    db_path: Path | str | None = None
) -> dict[str, Any] | None:
    """
    Retrieves full lifecycle metadata (including amendments) for a standard number.
    Returns None if the standard does not exist.
    """
    std = get_standard_by_number(standard_number, db_path=db_path)
    if not std:
        return None
    lc = get_lifecycle_by_standard_id(std["id"], db_path=db_path)
    amendments = get_amendments_by_standard_id(std["id"], db_path=db_path)
    return {
        "standard_id": std["id"],
        "standard_number": std["standard_number"],
        "title": std["title"],
        "year_of_publication": std.get("year_of_publication"),
        "edition": std.get("edition"),
        "lifecycle_status": lc["lifecycle_status"] if lc else "UNKNOWN",
        "reaffirmed_year": lc["reaffirmed_year"] if lc else None,
        "reviewed_year": lc["reviewed_year"] if lc else None,
        "amendment_count": lc["amendment_count"] if lc else 0,
        "supersedes": lc["supersedes"] if lc else None,
        "superseded_by": lc["superseded_by"] if lc else std.get("superseded_by"),
        "source_url": lc["source_url"] if lc else std.get("source_url"),
        "verification_date": lc["verification_date"] if lc else None,
        "verification_note": lc["verification_note"] if lc else None,
        "amendments": amendments,
    }


def get_compliance_by_standard_id(
    standard_id: int,
    db_path: Path | str | None = None
) -> dict[str, Any] | None:
    """
    Retrieves compliance and QCO metadata for a given standard id.
    Returns None if no compliance record exists.
    """
    with get_db_cursor(db_path) as cursor:
        cursor.execute(
            "SELECT * FROM standard_compliance WHERE standard_id = ?",
            (standard_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return dict(row)


def get_compliance_by_number(
    standard_number: str,
    db_path: Path | str | None = None
) -> dict[str, Any] | None:
    """
    Retrieves compliance metadata for a standard number.
    Returns None if the standard does not exist.
    """
    std = get_standard_by_number(standard_number, db_path=db_path)
    if not std:
        return None
    comp = get_compliance_by_standard_id(std["id"], db_path=db_path)
    return {
        "standard_id": std["id"],
        "standard_number": std["standard_number"],
        "certification_status": comp["certification_status"] if comp else "UNKNOWN",
        "certification_scheme": comp["certification_scheme"] if comp else None,
        "qco_status": comp["qco_status"] if comp else "UNKNOWN",
        "qco_reference": comp["qco_reference"] if comp else None,
        "qco_title": comp["qco_title"] if comp else None,
        "issuing_authority": comp["issuing_authority"] if comp else None,
        "enforcement_date": comp["enforcement_date"] if comp else None,
        "evidence_source_title": comp["evidence_source_title"] if comp else None,
        "evidence_source_url": comp["evidence_source_url"] if comp else None,
        "evidence_source_type": comp["evidence_source_type"] if comp else None,
        "notes": comp["notes"] if comp else None,
        "last_verified": comp["last_verified"] if comp else None,
    }
