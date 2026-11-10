from dotenv import load_dotenv
from anthropic import Anthropic

from app.retrieval import search

load_dotenv()
client = Anthropic()

MODEL = "claude-haiku-5-5"
MIN_SIMILARITY = 0.20
HANDOFF_MESSAGE = "I do not have the answer to that question, but I can connect you with our team to help you out with that. Would you like me to do that for you?"

SYSTEM_PROMPT = """You are the website assistant for Cedar Ridge Roofing & Renovation.
Rules:
- Answer only from the provided sources.
- Put the source number after each fact, like [1].
- If the sources don't contain the answer, say so and offer to connect the customer with our team.
- If the sources answer only part of the question, answer that part and say what's missing.
- Never promise anything that is not written in the sources.
- Be short and friendly."""


def build_context(chunks):
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(f"[{i}] {chunk['source']} > {chunk['section']}\n{chunk['content']}")
    return "\n\n".join(parts)


def answer_question(question):
    # 1. find the most relevant chunks
    chunks = search(question)

    # 2. handoff: best score too low → don't call Claude
    if chunks[0]["similarity"] < MIN_SIMILARITY:
        return {"answer": HANDOFF_MESSAGE, "sources": [], "handoff": True}

    # 3. ask Claude, giving it the sources + the question
    context = build_context(chunks)
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Sources:\n{context}\n\nQuestion: {question}"}],
    )

    # 4. take only the text block (skip thinking blocks)
    answer = ""
    for block in response.content:
        if block.type == "text":
            answer = block.text

    # 5. list the sources for the citations
    sources = [f"{c['source']} > {c['section']}" for c in chunks]

    return {"answer": answer, "sources": sources, "handoff": False}


if __name__ == "__main__":
    for q in ["How much are gutter guards, and do you install solar panels?"]:
        result = answer_question(q)
        print(result["answer"])
