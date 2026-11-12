import logging
import time

from fastapi import FastAPI, HTTPException

from app.answer import answer_question
from app.costs import estimate_cost
from app.lead import extract_lead, qualify_lead
from app.schemas import ChatRequest, ChatResponse, LeadRequest, LeadResponse
from app.logs import save_log

logging.basicConfig(level=logging.INFO)                    

app = FastAPI(title="Cedar Ridge AI Assistant")
logger = logging.getLogger(__name__)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    start = time.perf_counter()                             
    try:
        result = answer_question(request.question)
    except Exception:
        logger.exception("chat failed")
        raise HTTPException(status_code=503, detail="The assistant is temporarily unavailable. Please try again or contact our team.")

    seconds = time.perf_counter() - start
    usage = result["usage"]
    cost = estimate_cost(usage["input_tokens"], usage["output_tokens"])
    logger.info(f"chat | {seconds:.2f}s | in={usage['input_tokens']} out={usage['output_tokens']} "
                f"| ${cost:.6f} | handoff={result['handoff']}")
    save_log("chat", seconds, usage, cost, f"handoff={result['handoff']}")
    return result


@app.post("/qualify-lead", response_model=LeadResponse)
def qualify(request: LeadRequest):
    start = time.perf_counter()                                        
    try:
        lead, usage = extract_lead(request.conversation)              
        result = qualify_lead(lead)
    except Exception:
        logger.exception("qualify-lead failed")
        raise HTTPException(status_code=503, detail="Could not process the lead right now. Please try again.")

    seconds = time.perf_counter() - start                              
    cost = estimate_cost(usage["input_tokens"], usage["output_tokens"])
    logger.info(f"qualify-lead | {seconds:.2f}s | in={usage['input_tokens']} out={usage['output_tokens']} "
                f"| ${cost:.6f} | qualified={result['qualified']}")   
    save_log("qualify-lead", seconds, usage, cost, f"qualified={result['qualified']}")
    return {"lead": lead, "qualified": result["qualified"], "reasons": result["reasons"]}   
    
   