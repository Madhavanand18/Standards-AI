import sqlite3
import pytest
from pathlib import Path
import tempfile

from app.db.database import get_connection, init_db, get_all_standards, get_standard_by_number
from app.db.init_db import seed_database

def test_init_db_and_seeding():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db_path = Path(tmp.name)

    try:
        # Initialize schema
        init_db(tmp_db_path)

        # Seed data
        count = seed_database(db_path=tmp_db_path, reset=True)
        assert count == 15

        # Query all standards
        standards = get_all_standards(tmp_db_path)
        assert len(standards) == 15

        # Verify a specific standard
        is_1786 = get_standard_by_number("IS 1786:2008", tmp_db_path)
        assert is_1786 is not None
        assert "High Strength Deformed Steel Bars" in is_1786["title"]
        assert is_1786["category"] == "Reinforcement Steel / Construction"
        assert is_1786["status"] == "ACTIVE"
        assert isinstance(is_1786["keywords"], list)
        assert "TMT bars" in is_1786["keywords"]

        # Verify relationships table
        conn = get_connection(tmp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM standard_relationships")
        rel_count = cursor.fetchone()["cnt"]
        assert rel_count >= 4
        conn.close()
    finally:
        if tmp_db_path.exists():
            tmp_db_path.unlink()
