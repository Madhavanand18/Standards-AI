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

CREATE INDEX IF NOT EXISTS idx_standards_number ON standards(standard_number);
CREATE INDEX IF NOT EXISTS idx_standards_category ON standards(category);
CREATE INDEX IF NOT EXISTS idx_standards_status ON standards(status);
CREATE INDEX IF NOT EXISTS idx_rel_source ON standard_relationships(source_standard_id);
CREATE INDEX IF NOT EXISTS idx_rel_target ON standard_relationships(target_standard_id);
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
    """Retrieves standard by its standard_number."""
    with get_db_cursor(db_path) as cursor:
        cursor.execute("SELECT * FROM standards WHERE standard_number = ?", (standard_number,))
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
