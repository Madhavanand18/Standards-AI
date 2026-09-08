"""
Focused tests for Run 4A — BIS Standard Lifecycle & Amendment Intelligence.

Tests cover:
- Schema construction (StandardLifecycle, StandardAmendment)
- DB helpers: init, seed, get_lifecycle_by_number, get_amendments_by_standard_id
- LifecycleService methods
- API endpoint GET /api/v1/standards/{standard_number}/lifecycle
"""
import json
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# ── Helpers ──────────────────────────────────────────────────────────────────

SAMPLE_STANDARD = {
    "standard_number": "IS 1786:2008",
    "title": "High Strength Deformed Steel Bars — Specification",
    "year_of_publication": 2008,
    "edition": "Fourth Revision",
    "status": "ACTIVE",
    "superseded_by": None,
    "scope": "Covers deformed steel bars for use as reinforcement in concrete.",
    "department": "Civil",
    "category": "Reinforcement Steel",
    "keywords": ["TMT bars", "Fe 500"],
    "source_url": "https://standardsbis.bsbedge.com",
    "source_evidence_note": "BIS catalog",
}

SAMPLE_LIFECYCLE = {
    "standard_number": "IS 1786:2008",
    "lifecycle_status": "ACTIVE",
    "year_of_publication": 2008,
    "edition": "Fourth Revision",
    "reaffirmed_year": None,
    "reviewed_year": None,
    "amendment_count": 2,
    "supersedes": "IS 1786:1985",
    "superseded_by": None,
    "amendments": [
        {
            "amendment_number": 1,
            "year": 2012,
            "description": "Amendment No.1 for Fe 500D.",
            "source_url": "https://standardsbis.bsbedge.com",
            "verification_date": "2026-09-08",
        },
        {
            "amendment_number": 2,
            "year": 2018,
            "description": "Amendment No.2 for Fe 600.",
            "source_url": "https://standardsbis.bsbedge.com",
            "verification_date": "2026-09-08",
        },
    ],
    "source_url": "https://standardsbis.bsbedge.com",
    "verification_date": "2026-09-08",
    "verification_note": "Status confirmed ACTIVE from BIS portal.",
}


def _make_temp_db(
    standards: list | None = None,
    lifecycle_entries: list | None = None,
) -> tuple[Path, Path, Path]:
    """
    Creates temp files for standards, lifecycle, and a temp SQLite DB.
    Returns (seed_path, lifecycle_path, db_path).
    """
    tmpdir = Path(tempfile.mkdtemp())
    seed_path = tmpdir / "standards.json"
    lc_path = tmpdir / "lifecycle.json"
    db_path = tmpdir / "test.db"

    seed_path.write_text(
        json.dumps(standards if standards is not None else [SAMPLE_STANDARD], ensure_ascii=False),
        encoding="utf-8",
    )
    lc_path.write_text(
        json.dumps(lifecycle_entries if lifecycle_entries is not None else [SAMPLE_LIFECYCLE], ensure_ascii=False),
        encoding="utf-8",
    )
    return seed_path, lc_path, db_path


# ── Schema tests ──────────────────────────────────────────────────────────────

class TestStandardLifecycleSchema:
    def test_constructs_from_db_row(self):
        from app.schemas.lifecycle import StandardLifecycle

        row = {
            "standard_id": 1,
            "standard_number": "IS 1786:2008",
            "title": "High Strength Deformed Steel Bars",
            "year_of_publication": 2008,
            "edition": "Fourth Revision",
            "lifecycle_status": "ACTIVE",
            "reaffirmed_year": None,
            "reviewed_year": None,
            "amendment_count": 2,
            "supersedes": "IS 1786:1985",
            "superseded_by": None,
            "source_url": "https://standardsbis.bsbedge.com",
            "verification_date": "2026-09-08",
            "verification_note": "Confirmed.",
            "amendments": [
                {
                    "amendment_number": 1,
                    "year": 2012,
                    "description": "AMD 1",
                    "source_url": "https://standardsbis.bsbedge.com",
                    "verification_date": "2026-09-08",
                }
            ],
        }
        lc = StandardLifecycle.from_db_row(row)
        assert lc.standard_number == "IS 1786:2008"
        assert lc.lifecycle_status == "ACTIVE"
        assert lc.amendment_count == 2
        assert len(lc.amendments) == 1
        assert lc.amendments[0].amendment_number == 1
        assert lc.amendments[0].year == 2012
        assert lc.supersedes == "IS 1786:1985"
        assert lc.superseded_by is None

    def test_defaults_for_missing_fields(self):
        from app.schemas.lifecycle import StandardLifecycle

        row = {
            "standard_number": "IS 999:2000",
            "title": "Test Standard",
            "amendments": [],
        }
        lc = StandardLifecycle.from_db_row(row)
        assert lc.lifecycle_status == "UNKNOWN"
        assert lc.amendment_count == 0
        assert lc.amendments == []
        assert lc.reaffirmed_year is None


# ── DB helper tests ───────────────────────────────────────────────────────────

class TestLifecycleDatabaseHelpers:
    def test_seed_creates_lifecycle_and_amendments(self):
        from app.db.init_db import seed_database
        from app.db.database import get_lifecycle_by_number

        seed_path, lc_path, db_path = _make_temp_db()
        seed_database(
            seed_file_path=seed_path,
            seed_lifecycle_path=lc_path,
            db_path=db_path,
        )

        result = get_lifecycle_by_number("IS 1786:2008", db_path=db_path)
        assert result is not None
        assert result["lifecycle_status"] == "ACTIVE"
        assert result["amendment_count"] == 2
        assert result["supersedes"] == "IS 1786:1985"

    def test_amendments_stored_and_retrieved(self):
        from app.db.init_db import seed_database
        from app.db.database import get_lifecycle_by_number

        seed_path, lc_path, db_path = _make_temp_db()
        seed_database(
            seed_file_path=seed_path,
            seed_lifecycle_path=lc_path,
            db_path=db_path,
        )

        result = get_lifecycle_by_number("IS 1786:2008", db_path=db_path)
        amendments = result["amendments"]
        assert len(amendments) == 2
        # Amendments ordered by amendment_number ASC
        assert amendments[0]["amendment_number"] == 1
        assert amendments[0]["year"] == 2012
        assert amendments[1]["amendment_number"] == 2
        assert amendments[1]["year"] == 2018

    def test_get_lifecycle_by_number_returns_none_for_missing_standard(self):
        from app.db.init_db import seed_database
        from app.db.database import get_lifecycle_by_number

        seed_path, lc_path, db_path = _make_temp_db()
        seed_database(
            seed_file_path=seed_path,
            seed_lifecycle_path=lc_path,
            db_path=db_path,
        )

        result = get_lifecycle_by_number("IS 9999:1900", db_path=db_path)
        assert result is None

    def test_lifecycle_missing_data_gives_unknown_status(self):
        """
        Standard with no lifecycle record still returns a result (from standards table).
        lifecycle_status defaults to 'UNKNOWN' when no lifecycle row exists,
        because get_lifecycle_by_number returns 'UNKNOWN' only if lc is None.
        But the standards table also has a 'status' field.
        Verify that with empty lifecycle table, the result comes from the standards row.
        """
        from app.db.init_db import seed_database
        from app.db.database import get_lifecycle_by_number, get_lifecycle_by_standard_id

        # Seed with empty lifecycle file
        seed_path, lc_path, db_path = _make_temp_db(
            standards=[SAMPLE_STANDARD],
            lifecycle_entries=[],
        )
        seed_database(
            seed_file_path=seed_path,
            seed_lifecycle_path=lc_path,
            db_path=db_path,
        )

        # The standard exists, lifecycle helper row does NOT exist
        from app.db.database import get_standard_by_number
        std = get_standard_by_number("IS 1786:2008", db_path=db_path)
        assert std is not None

        lc_row = get_lifecycle_by_standard_id(std["id"], db_path=db_path)
        assert lc_row is None  # No lifecycle record seeded

        # get_lifecycle_by_number returns UNKNOWN when no lifecycle row
        result = get_lifecycle_by_number("IS 1786:2008", db_path=db_path)
        assert result is not None  # standard itself exists
        assert result["lifecycle_status"] == "UNKNOWN"  # defaults to UNKNOWN when no lc row
        assert result["amendments"] == []

    def test_seed_idempotent_on_reseed(self):
        """Re-seeding should not duplicate lifecycle or amendment records."""
        from app.db.init_db import seed_database
        from app.db.database import get_amendments_by_standard_id, get_standard_by_number

        seed_path, lc_path, db_path = _make_temp_db()

        seed_database(seed_file_path=seed_path, seed_lifecycle_path=lc_path, db_path=db_path)
        seed_database(seed_file_path=seed_path, seed_lifecycle_path=lc_path, db_path=db_path)

        std = get_standard_by_number("IS 1786:2008", db_path=db_path)
        amendments = get_amendments_by_standard_id(std["id"], db_path=db_path)
        assert len(amendments) == 2  # must not be duplicated


# ── LifecycleService tests ────────────────────────────────────────────────────

class TestLifecycleService:
    def _seeded_service(self):
        from app.db.init_db import seed_database
        from app.services.lifecycle import LifecycleService

        seed_path, lc_path, db_path = _make_temp_db()
        seed_database(
            seed_file_path=seed_path,
            seed_lifecycle_path=lc_path,
            db_path=db_path,
        )
        return LifecycleService(db_path=db_path)

    def test_get_lifecycle_returns_correct_data(self):
        svc = self._seeded_service()
        lc = svc.get_lifecycle("IS 1786:2008")
        assert lc is not None
        assert lc.standard_number == "IS 1786:2008"
        assert lc.lifecycle_status == "ACTIVE"
        assert lc.amendment_count == 2
        assert len(lc.amendments) == 2

    def test_get_lifecycle_returns_none_for_unknown(self):
        svc = self._seeded_service()
        lc = svc.get_lifecycle("IS 0000:0000")
        assert lc is None

    def test_is_current_returns_true_for_active(self):
        svc = self._seeded_service()
        assert svc.is_current("IS 1786:2008") is True

    def test_is_current_returns_none_for_unknown_standard(self):
        svc = self._seeded_service()
        assert svc.is_current("IS 9999:1111") is None

    def test_get_lifecycle_dict_is_serialisable(self):
        import json
        svc = self._seeded_service()
        d = svc.get_lifecycle_dict("IS 1786:2008")
        assert d is not None
        # Must serialize without error
        serialized = json.dumps(d)
        assert "IS 1786:2008" in serialized


# ── API endpoint tests ────────────────────────────────────────────────────────

class TestLifecycleAPIEndpoint:
    @pytest.fixture(autouse=True)
    def _seed_and_patch(self, tmp_path, monkeypatch):
        """Seed a temp DB and patch the LifecycleService to use it."""
        from app.db.init_db import seed_database

        seed_path = tmp_path / "standards.json"
        lc_path = tmp_path / "lifecycle.json"
        db_path = tmp_path / "test.db"
        seed_path.write_text(json.dumps([SAMPLE_STANDARD]), encoding="utf-8")
        lc_path.write_text(json.dumps([SAMPLE_LIFECYCLE]), encoding="utf-8")

        seed_database(
            seed_file_path=seed_path,
            seed_lifecycle_path=lc_path,
            db_path=db_path,
        )

        # Patch the module-level lifecycle service used by the router
        from app.services.lifecycle import LifecycleService
        import app.api.v1.lifecycle as lc_module

        patched_svc = LifecycleService(db_path=db_path)
        monkeypatch.setattr(lc_module, "_lifecycle_service", patched_svc)

    @pytest.fixture
    def client(self):
        from app.main import app
        return TestClient(app)

    def test_lifecycle_endpoint_returns_200(self, client):
        resp = client.get("/api/v1/standards/IS 1786:2008/lifecycle")
        assert resp.status_code == 200

    def test_lifecycle_endpoint_returns_correct_fields(self, client):
        resp = client.get("/api/v1/standards/IS 1786:2008/lifecycle")
        data = resp.json()
        assert data["standard_number"] == "IS 1786:2008"
        assert data["lifecycle_status"] == "ACTIVE"
        assert data["amendment_count"] == 2
        assert len(data["amendments"]) == 2
        assert data["supersedes"] == "IS 1786:1985"

    def test_lifecycle_endpoint_amendments_ordered(self, client):
        resp = client.get("/api/v1/standards/IS 1786:2008/lifecycle")
        data = resp.json()
        amds = data["amendments"]
        assert amds[0]["amendment_number"] == 1
        assert amds[1]["amendment_number"] == 2

    def test_lifecycle_endpoint_404_for_unknown(self, client):
        resp = client.get("/api/v1/standards/IS 0000:0000/lifecycle")
        assert resp.status_code == 404
        assert "lifecycle record" in resp.json()["detail"].lower()

    def test_lifecycle_endpoint_includes_verification_note(self, client):
        resp = client.get("/api/v1/standards/IS 1786:2008/lifecycle")
        data = resp.json()
        assert data["verification_note"] is not None
        assert "BIS" in data["verification_note"] or "portal" in data["verification_note"]
