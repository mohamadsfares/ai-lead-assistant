import re

from dotenv import load_dotenv
from anthropic import Anthropic

from app.config import MODEL
from app.retrieval import search

load_dotenv()
client = Anthropic(timeout=30)

MIN_SIMILARITY = 0.20
HANDOFF_MARKER = "[HANDOFF]"
HANDOFF_MESSAGE = "I do not have the answer to that question, but I can connect you with our team to help you out with that. Would you like me to do that for you?"

SYSTEM_PROMPT = """You are the website assistant for Cedar Ridge Roofing & Renovation.
Rules:
- Answer only from the provided sources.
- Put the source number after each fact, like [1].
- If the sources don't contain the answer, say so and offer to connect the customer with our team.
- If the sources answer only part of the question, answer that part and say what's missing.
- Only if the sources do not contain information the customer asked for, end your reply with [HANDOFF] on its own line. Do not add it when the sources answered the question, even if you also suggest a quote or an inspection.
- Never promise anything that is not written in the sources.
- A clear "no" from the sources (a service we don't offer, an area we don't serve) is a full answer: do not add [HANDOFF].
- Be short and friendly."""


def build_context(chunks):
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(f"[{i}] {chunk['source']} > {chunk['section']}\n{chunk['content']}")
    return "\n\n".join(parts)


def cited_sources(answer, chunks):
    numbers = sorted({int(n) for n in re.findall(r"\[(\d+)\]", answer)})
    sources = []
    for n in numbers:
        if 1 <= n <= len(chunks):
            chunk = chunks[n - 1]
            sources.append(f"[{n}] {chunk['source']} > {chunk['section']}")
    return sources


def answer_question(question):
    # 1. find the most relevant chunks
    chunks = search(question)

    # 2. handoff: best score too low → don't call Claude
    if not chunks or chunks[0]["similarity"] < MIN_SIMILARITY:
        return {"answer": HANDOFF_MESSAGE, "sources": [], "handoff": True, "usage": {"input_tokens": 0, "output_tokens": 0}}

    # 3. ask Claude, giving it the sources + the question
    context = build_context(chunks)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Sources:\n{context}\n\nQuestion: {question}"}],
    )
    usage = {"input_tokens": response.usage.input_tokens,
             "output_tokens": response.usage.output_tokens}

    # 4. take only the text block (skip thinking blocks)
    answer = "".join(block.text for block in response.content if block.type == "text").strip()

    # 5. did Claude say it couldn't fully answer? Remove the marker from the text
    handoff = HANDOFF_MARKER in answer
    answer = answer.replace(HANDOFF_MARKER, "").strip()
    if not answer:
        return {"answer": HANDOFF_MESSAGE, "sources": [], "handoff": True, "usage": usage}

    # 6. keep only the sources the answer actually cites
    sources = cited_sources(answer, chunks)

    return {"answer": answer, "sources": sources, "handoff": handoff, "usage": usage}


if __name__ == "__main__":
    for q in ["Do you offer a discount for seniors?", "How much does a new roof cost?"]:
        result = answer_question(q)
        print(result["answer"])
        print(result["sources"])
        print(result["handoff"])
        print("---")