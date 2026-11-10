from typing import Literal
from pydantic import BaseModel



class LeadSummary(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    town: str | None = None
    budget: str | None = None
    service: Literal["roof_replacement", "roof_repair", "storm_damage", "gutters", "siding", "windows", "kitchen_remodel", "bathroom_remodel", "other"]| None = None
    urgency: Literal["emergency", "soon", "flexible", "unknown"] = "unknown"
    summary: str 


if __name__ == "__main__":
    good = LeadSummary(name="Sara", town="Dublin", urgency="emergency", summary="Roof leak after storm")
    print(good)

    bad = LeadSummary(urgency="urgent!!", summary="Test")
    print(bad)