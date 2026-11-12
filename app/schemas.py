from typing import Literal
from pydantic import BaseModel
from pydantic import BaseModel, Field



class LeadSummary(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    town: str | None = None
    budget: str | None = None
    service: Literal["roof_replacement", "roof_repair", "storm_damage", "gutters", "siding", "windows", "kitchen_remodel", "bathroom_remodel", "other"]| None = None
    urgency: Literal["emergency", "soon", "flexible", "unknown"] = Field(
        "unknown",
        description="emergency = active leak or storm damage now; soon = wants work within about a month; "
                    "flexible = no rush or a later season; unknown = not mentioned",
    )
    summary: str 


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length= 1000)


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    handoff: bool


class LeadRequest(BaseModel):
    conversation: str = Field(min_length=1, max_length=5000)


class LeadResponse(BaseModel):
    lead: LeadSummary
    qualified: bool
    reasons: list[str]

if __name__ == "__main__":
    good = LeadSummary(name="Sara", town="Dublin", urgency="emergency", summary="Roof leak after storm")
    print(good)

    bad = LeadSummary(urgency="urgent!!", summary="Test")
    print(bad)