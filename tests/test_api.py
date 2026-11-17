from fastapi.testclient import TestClient


import app.main
from app.main import app as api 


client= TestClient(api)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "Cedar Ridge AI Assistant"}


def test_chat_rejects_empty_question():
    response = client.post("/chat", json={"question":""})
    assert response.status_code == 422


def test_chat_rejects_too_long_question():
    response = client.post("/chat", json={"question" :"x" * 1001})
    assert response.status_code == 422

def test_chat_returns_answer_without_internal_usage(monkeypatch):
    def fake_answer(question):
        return {"answer": "Test answer [1]", "sources": ["pricing.md > Roofing"],
                "handoff": False, "usage": {"input_tokens": 10, "output_tokens": 5}}

    monkeypatch.setattr(app.main, "answer_question", fake_answer)
    monkeypatch.setattr(app.main, "save_log", lambda *args: None)

    response = client.post("/chat", json={"question": "How much is a roof?"})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Test answer [1]"
    assert "usage" not in body          # internal costs must stay hidden


def test_chat_returns_503_when_answering_fails(monkeypatch):
    def broken_answer(question):
        raise RuntimeError("Claude is down")

    monkeypatch.setattr(app.main, "answer_question", broken_answer)

    response = client.post("/chat", json={"question": "How much is a roof?"})
    assert response.status_code == 503
    assert "Claude" not in response.json()["detail"]   # no internal details leaked