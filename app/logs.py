import logging

from app.db import supabase

logger = logging.getLogger(__name__)


def save_log(endpoint, seconds, usage, cost, outcome):

    try:
        supabase.table("request_logs").insert({
            "endpoint": endpoint,
            "latency_s": round(seconds, 3),
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "cost_usd": cost,
            "outcome": outcome,
        }).execute()
    except Exception:
        logger.warning("could not save request log", exc_info=True)