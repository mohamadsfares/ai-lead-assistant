from dotenv import load_dotenv
from anthropic import Anthropic
from pydantic import ValidationError

from app.schemas import LeadSummary

load_dotenv()
client = Anthropic()

MODEL = "claude-haiku-5-5"

LEAD_TOOL = {
    "name": "save_lead",
    "description": "Save the lead details of a customer from a website chat conversation.",
    "input_schema": LeadSummary.model_json_schema(),
}

LEAD_SYSTEM_PROMPT = """You extract lead details for Cedar Ridge Roofing & Renovation.
Rules:
- Read the conversation and fill in the save_lead tool.
- Use only information the customer actually said.
- If a detail was not mentioned, leave it empty. Never guess.
- Write the summary as one short sentence describing what the customer wants."""


CORE_TOWNS={"columbus","dublin","westerville","hilliard","grove city","gahanna","worthington","upper arlington","reynoldsburg","pickerington"}
EXTENDED_TOWNS = {"delaware", "newark", "marysville", "lancaster"}


def extract_lead(conversation):
    for attempt in range(2):
        response= client.messages.create(
            model=MODEL, 
              max_tokens=1000, 
              system=LEAD_SYSTEM_PROMPT,
              messages=[{"role": "user", "content": conversation}],
              tools=[LEAD_TOOL],
              tool_choice ={"type": "tool", "name": "save_lead"},
              )
        for block in response.content:
            if block.type == "tool_use":
                try:
                    return LeadSummary(**block.input)
                except ValidationError:
                    continue
    
    raise ValueError("Could not extract a valid lead after 2 attempts")




def qualify_lead(lead):
    reasons=[]
    if not lead.phone and not lead.email:
        reasons.append("no contact details")
    if lead.town is None:
        reasons.append("town unknown")
    elif lead.town.lower() not in CORE_TOWNS and lead.town.lower() not in EXTENDED_TOWNS:
        reasons.append("outside service area")
    if  lead.service is None or lead.service == "other":
        reasons.append("unclear or not offered")
    return {"qualified": len(reasons) == 0, "reasons": reasons}
    



if __name__ == "__main__":
    chat = "Hi, I'm Rami from Cincinnati. Do you install solar panels? You can email me at rami@example.com."
    lead = extract_lead(chat)
    print(lead)
    print(qualify_lead(lead))