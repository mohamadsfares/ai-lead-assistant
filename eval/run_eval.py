import json
import statistics
import time

from app.answer import answer_question
from app.retrieval import search

HANDOFF_PHRASES = ["don't have", "do not have", "connect you", "our team",
                   "don't say", "do not say", "not mentioned", "no information"]

with open("eval/questions.json", encoding="utf-8") as f:
    questions = json.load(f)


def retrieval_hit(q):
    if not q["expected_sources"]:
        return None
    chunks = search(q["question"])
    found = [f"{c['source']} > {c['section']}" for c in chunks]
    if q["type"] == "multi_part":
        return all(s in found for s in q["expected_sources"])
    return any(s in found for s in q["expected_sources"])


def fact_hit(q, result):
    if not q["must_contain_any"]:
        return None
    if result["handoff"]:
        return False
    text = result["answer"].lower()
    return any(word.lower() in text for word in q["must_contain_any"])


def handoff_ok(q, result):
    if q["should_handoff"]:
        return result["handoff"] or any(p in result["answer"].lower() for p in HANDOFF_PHRASES)
    return not result["handoff"]


def summarize(results, key):
    # keep only the questions where this score was checked (skip None)
    values = [r[key] for r in results if r[key] is not None]
    # True counts as 1, False as 0 → sum = number of passes
    return f"{sum(values)} / {len(values)}"


if __name__ == "__main__":
    results = []

    for q in questions:
        start = time.perf_counter()
        result = answer_question(q["question"])
        seconds = time.perf_counter() - start

        r_hit = retrieval_hit(q)
        f_hit = fact_hit(q, result)
        h_ok = handoff_ok(q, result)

        print(q["id"], q["type"], "| retrieval:", r_hit, "| fact:", f_hit,
              "| handoff:", h_ok, "|", round(seconds, 1), "s")

        results.append({"retrieval": r_hit, "fact": f_hit, "handoff": h_ok, "seconds": seconds})

    print("---- SUMMARY ----")
    print("Retrieval hit:  ", summarize(results, "retrieval"))
    print("Correct facts:  ", summarize(results, "fact"))
    print("Handoff correct:", summarize(results, "handoff"))
    print("Median latency: ", round(statistics.median([r["seconds"] for r in results]), 1), "s")

