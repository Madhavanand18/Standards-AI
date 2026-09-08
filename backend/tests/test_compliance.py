"""
Focused tests for Run 5A — Procurement Compliance Foundation.

Tests cover:
- Schema construction (StandardCompliance, CertificationStatus, QCOStatus)
- DB helpers: init, seed, get_compliance_by_standard_id, get_compliance_by_number
- ComplianceService methods: get_compliance, is_mandatory, get_compliance_dict
- API endpoint GET /api/v1/standards/{standard_number}/compliance
- Distinction between standard applicability and mandatory certification
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.compliance import StandardCompliance, CertificationStatus, QCOStatus
from app.services.compliance import ComplianceService
from app.db.database import (
    get_compliance_by_number,
    get_compliance_by_standard_id,
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

    def test_schema_from_db_row(self):
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
            "evidence_source_title": "Gazette Notification",
            "evidence_source_url": "https://steel.gov.in/en/quality-control-orders",
            "evidence_source_type": "GAZETTE_NOTIFICATION",
            "notes": "Compulsory Scheme-I certification",
            "last_verified": "2026-09-08",
        }
        comp = StandardCompliance.from_db_row(row)
        assert comp.standard_id == 10
        assert comp.standard_number == "IS 1786:2008"
        assert comp.certification_status == "MANDATORY"
        assert comp.certification_scheme == "Scheme I (ISI Mark Scheme)"
        assert comp.qco_status == "APPLICABLE"
        assert comp.issuing_authority == "Ministry of Steel"


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

    def test_get_compliance_by_number_design_code(self):
        """IS 456:2000 is a design code with NOT_IDENTIFIED status rather than fabricated claims."""
        comp = get_compliance_by_number("IS 456:2000")
        assert comp is not None
        assert comp["certification_status"] == "NOT_IDENTIFIED"
        assert comp["qco_status"] == "NOT_IDENTIFIED"
        assert comp["qco_reference"] is None

    def test_get_compliance_by_number_unknown_standard(self):
        comp = get_compliance_by_number("IS 999999:2099")
        assert comp is None

    def test_get_compliance_by_standard_id(self):
        std = get_standard_by_number("IS 2062:2011")
        assert std is not None
        comp_row = get_compliance_by_standard_id(std["id"])
        assert comp_row is not None
        assert comp_row["certification_status"] == "MANDATORY"


class TestComplianceService:
    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.service = ComplianceService()

    def test_get_compliance_returns_model(self):
        comp = self.service.get_compliance("IS 1786:2008")
        assert isinstance(comp, StandardCompliance)
        assert comp.certification_status == "MANDATORY"
        assert comp.qco_status == "APPLICABLE"

    def test_is_mandatory_logic(self):
        # Mandatory product standards under QCO
        assert self.service.is_mandatory("IS 1786:2008") is True
        assert self.service.is_mandatory("IS 2062:2011") is True
        assert self.service.is_mandatory("IS 269:2015") is True

        # Non-QCO / code of practice standard
        assert self.service.is_mandatory("IS 456:2000") is False
        assert self.service.is_mandatory("IS 800:2007") is False

        # Non-existent standard
        assert self.service.is_mandatory("IS 0000:0000") is False

    def test_get_compliance_dict(self):
        d = self.service.get_compliance_dict("IS 2925:1984")
        assert isinstance(d, dict)
        assert d["standard_number"] == "IS 2925:1984"
        assert d["certification_status"] == "MANDATORY"
        assert d["issuing_authority"] is not None


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
