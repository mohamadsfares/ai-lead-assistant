from app.lead import normalize_town, qualify_lead
from app.schemas import LeadSummary


def test_normalize_town_cleans_messy_input():
    assert normalize_town("Dublin ") == "dublin"
    assert normalize_town("Columbus, OH") == "columbus"
    assert normalize_town("Grove City, Ohio") == "grove city"
    assert normalize_town("") is None
    assert normalize_town(None) is None


def test_qualified_lead_has_no_reasons():
    lead = LeadSummary(name="Sara", phone="614-555-0101", town="Dublin, OH",
                       service="storm_damage", summary="Roof leak after storm")
    result = qualify_lead(lead)
    assert result["qualified"] is True
    assert result["reasons"] == []


def test_lead_without_contact_is_not_qualified():
    lead = LeadSummary(name="Ali", town="Westerville", service="roof_replacement",
                       summary="New roof next spring")
    result = qualify_lead(lead)
    assert result["qualified"] is False
    assert result["reasons"] == ["no contact details"]


def test_lead_outside_area_with_unoffered_service_gets_two_reasons():
    lead = LeadSummary(email="rami@example.com", town="Cincinnati", service="other",
                       summary="Asks about solar panels")
    result = qualify_lead(lead)
    assert result["qualified"] is False
    assert "outside service area" in result["reasons"]
    assert "unclear or not offered" in result["reasons"]


def test_missing_town_is_unknown_not_outside():
    lead = LeadSummary(phone="614-555-0199", service="gutters", summary="Gutter repair")
    result = qualify_lead(lead)
    assert result["reasons"] == ["town unknown"]