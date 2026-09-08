"""
Focused tests for Run 5B — Verified Procurement Compliance & QCO Intelligence.

Tests cover:
- Schema construction (StandardCompliance, ComplianceEvent, CertificationStatus, QCOStatus)
- DB helpers: init, seed, get_compliance_by_standard_id, get_compliance_events_by_standard_id, get_compliance_by_number
- Version-aware compliance (e.g. IS 15298 (Part 2):2016 referenced in QCO vs 2024 revised standard transition)
- ComplianceService methods: get_compliance, is_mandatory, get_compliance_dict
- API endpoint GET /api/v1/standards/{standard_number}/compliance with milestone timeline events
- Accurate distinction between mandatory QCO products, voluntary certification, and design codes
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.compliance import (
    StandardCompliance,
    ComplianceEvent,
    CertificationStatus,
    QCOStatus,
)
from app.services.compliance import ComplianceService
from app.db.database import (
    get_compliance_by_number,
    get_compliance_by_standard_id,
    get_compliance_events_by_standard_id,
    get_standard_by_number,
)

client = TestClient(app)


class TestComplianceSchema:
    def test_schema_defaults(self):
        comp = StandardCompliance(standard_number="IS 9999:2020")
        assert comp.standard_number == "IS 9999:2020"
        assert comp.certification_status == CertificationStatus.UNKNOWN.value
        assert comp.qco_status == QCOStatus.UNKNOWN.value
        assert comp.certification_scheme is None
        assert comp.qco_reference is None
        assert comp.evidence_source_url is None
        assert comp.events == []

    def test_schema_from_db_row_with_events(self):
        row = {
            "standard_id": 10,
            "standard_number": "IS 1786:2008",
            "certification_status": "MANDATORY",
            "certification_scheme": "Scheme I (ISI Mark Scheme)",
            "qco_status": "APPLICABLE",
            "qco_reference": "Steel and Steel Products QCO",
            "qco_title": "Steel QCO 2020",
            "issuing_authority": "Ministry of Steel",
            "enforcement_date": "2020-05-27",
            "referenced_standard_edition": "IS 1786:2008",
            "latest_standard_version": "IS 1786:2008",
            "qco_clause_standard_applicability": "Latest version applies.",
            "evidence_source_title": "Gazette Notification",
            "evidence_source_url": "https://steel.gov.in/en/quality-control-orders",
            "evidence_source_type": "GAZETTE_NOTIFICATION",
            "notes": "Compulsory Scheme-I certification",
            "last_verified": "2026-09-08",
            "events": [
                {
                    "id": 1,
                    "event_date": "2020-05-27",
                    "event_type": "SUPERSEDING_QCO",
                    "title": "Steel QCO 2020",
                    "description": "Notified compulsory certification.",
                    "reference_doc": "S.O. 1673(E)",
                    "source_url": "https://steel.gov.in/en/quality-control-orders",
                }
            ],
        }
        comp = StandardCompliance.from_db_row(row)
        assert comp.standard_id == 10
        assert comp.standard_number == "IS 1786:2008"
        assert comp.certification_status == "MANDATORY"
        assert comp.certification_scheme == "Scheme I (ISI Mark Scheme)"
        assert comp.qco_status == "APPLICABLE"
        assert comp.issuing_authority == "Ministry of Steel"
        assert len(comp.events) == 1
        assert comp.events[0].event_type == "SUPERSEDING_QCO"


class TestComplianceDatabase:
    def test_get_compliance_by_number_mandatory_standard(self):
        """IS 1786:2008 has mandatory QCO compliance in seed data."""
        comp = get_compliance_by_number("IS 1786:2008")
        assert comp is not None
        assert comp["certification_status"] == "MANDATORY"
        assert comp["qco_status"] == "APPLICABLE"
        assert "Scheme I" in (comp["certification_scheme"] or "")
        assert comp["issuing_authority"] is not None
        assert comp["evidence_source_url"] is not None
        assert comp["last_verified"] is not None
        assert comp["qco_clause_standard_applicability"] is not None
        assert len(comp["events"]) >= 1

    def test_get_compliance_by_number_design_code(self):
        """IS 456:2000 is a design code with NOT_IDENTIFIED status rather than fabricated claims."""
        comp = get_compliance_by_number("IS 456:2000")
        assert comp is not None
        assert comp["certification_status"] == "NOT_IDENTIFIED"
        assert comp["qco_status"] == "NOT_IDENTIFIED"
        assert comp["qco_reference"] is None

    def test_get_compliance_by_number_voluntary_standard(self):
        """IS 1077:2020 has voluntary Scheme I certification without mandatory QCO."""
        comp = get_compliance_by_number("IS 1077:2020")
        assert comp is not None
        assert comp["certification_status"] == "VOLUNTARY"
        assert comp["qco_status"] == "NOT_IDENTIFIED"
        assert "Scheme I" in (comp["certification_scheme"] or "")

    def test_get_compliance_by_number_unknown_standard(self):
        comp = get_compliance_by_number("IS 999999:2099")
        assert comp is None

    def test_get_compliance_by_standard_id(self):
        std = get_standard_by_number("IS 2062:2011")
        assert std is not None
        comp_row = get_compliance_by_standard_id(std["id"])
        assert comp_row is not None
        assert comp_row["certification_status"] == "MANDATORY"

    def test_get_compliance_events_by_standard_id(self):
        std = get_standard_by_number("IS 15298 (Part 2):2016")
        assert std is not None
        events = get_compliance_events_by_standard_id(std["id"])
        assert len(events) >= 3
        event_types = [e["event_type"] for e in events]
        assert "INITIAL_QCO" in event_types
        assert "ENFORCEMENT" in event_types
        assert "REVISED_STANDARD" in event_types or "IMPLEMENTATION_GUIDELINE" in event_types


class TestVersionAwareCompliance:
    def test_is15298_part2_version_transition_intelligence(self):
        """
        Special Audit Case: IS 15298 (Part 2) PPE safety footwear.
        The 2020 QCO referenced the 2016 version; BIS later published the 2024 revision
        with implementation guidelines in Jan 2025.
        """
        comp = get_compliance_by_number("IS 15298 (Part 2):2016")
        assert comp is not None
        assert comp["certification_status"] == "MANDATORY"
        assert comp["qco_status"] == "APPLICABLE"
        assert "2016" in comp["referenced_standard_edition"]
        assert "2024" in comp["latest_standard_version"]
        assert comp["qco_clause_standard_applicability"] is not None

        # Verify milestone events record both QCO order and 2024 revision / 2025 guidelines
        event_descs = " ".join([e["description"] for e in comp["events"]])
        assert "2024" in event_descs or "2025" in event_descs


class TestComplianceService:
    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.service = ComplianceService()

    def test_get_compliance_returns_model(self):
        comp = self.service.get_compliance("IS 1786:2008")
        assert isinstance(comp, StandardCompliance)
        assert comp.certification_status == "MANDATORY"
        assert comp.qco_status == "APPLICABLE"
        assert len(comp.events) >= 1

    def test_is_mandatory_logic(self):
        # Mandatory product standards under QCO
        assert self.service.is_mandatory("IS 1786:2008") is True
        assert self.service.is_mandatory("IS 2062:2011") is True
        assert self.service.is_mandatory("IS 269:2015") is True
        assert self.service.is_mandatory("IS 694:2010") is True
        assert self.service.is_mandatory("IS 4984:2016") is True
        assert self.service.is_mandatory("IS 15298 (Part 2):2016") is True

        # Voluntary or Non-QCO / code of practice standard
        assert self.service.is_mandatory("IS 456:2000") is False
        assert self.service.is_mandatory("IS 800:2007") is False
        assert self.service.is_mandatory("IS 10262:2019") is False
        assert self.service.is_mandatory("IS 1077:2020") is False

        # Non-existent standard
        assert self.service.is_mandatory("IS 0000:0000") is False

    def test_get_compliance_dict(self):
        d = self.service.get_compliance_dict("IS 2925:1984")
        assert isinstance(d, dict)
        assert d["standard_number"] == "IS 2925:1984"
        assert d["certification_status"] == "MANDATORY"
        assert d["issuing_authority"] is not None
        assert isinstance(d["events"], list)


class TestComplianceAPIEndpoint:
    def test_get_compliance_endpoint_200(self):
        response = client.get("/api/v1/standards/IS 1786:2008/compliance")
        assert response.status_code == 200
        data = response.json()
        assert data["standard_number"] == "IS 1786:2008"
        assert data["certification_status"] == "MANDATORY"
        assert data["qco_status"] == "APPLICABLE"
        assert data["certification_scheme"] == "Scheme I (ISI Mark Scheme)"
        assert data["issuing_authority"] == "Ministry of Steel, Government of India"
        assert data["evidence_source_url"] is not None
        assert data["evidence_source_type"] == "GAZETTE_NOTIFICATION"
        assert "events" in data
        assert len(data["events"]) >= 1

    def test_get_compliance_endpoint_version_awareness(self):
        response = client.get("/api/v1/standards/IS 15298 (Part 2):2016/compliance")
        assert response.status_code == 200
        data = response.json()
        assert data["certification_status"] == "MANDATORY"
        assert "2016" in data["referenced_standard_edition"]
        assert "2024" in data["latest_standard_version"]
        assert len(data["events"]) >= 3

    def test_get_compliance_endpoint_encoded_url(self):
        response = client.get("/api/v1/standards/IS%202062%3A2011/compliance")
        assert response.status_code == 200
        data = response.json()
        assert data["standard_number"] == "IS 2062:2011"
        assert data["certification_status"] == "MANDATORY"

    def test_get_compliance_endpoint_404_for_unknown(self):
        response = client.get("/api/v1/standards/IS%2099999/compliance")
        assert response.status_code == 404
        assert "No compliance record found" in response.json()["detail"]
