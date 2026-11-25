import requests
from streamlit.testing.v1 import AppTest

APP = "../frontend/streamlit_app.py"


class FakeResponse:
    def __init__(self, data, status_code=200):
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(response=self)


def fake_api(monkeypatch, response):
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: FakeResponse({"status": "ok"}))
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: response)


def test_page_shows_welcome_and_example_buttons(monkeypatch):
    fake_api(monkeypatch, FakeResponse({}))
    at = AppTest.from_file(APP).run()
    assert not at.exception
    assert len(at.button) == 4


def test_question_shows_answer_and_cited_sources(monkeypatch):
    data = {"answer": "A new roof costs $9,500 to $22,000 [1].",
            "sources": ["[1] pricing.md > Roofing"], "handoff": False}
    fake_api(monkeypatch, FakeResponse(data))
    at = AppTest.from_file(APP).run()
    at.chat_input[0].set_value("How much is a new roof?").run()
    assert not at.exception
    assert any("$9,500" in m.value for m in at.markdown)
    assert at.expander[0].label == "Sources"


def test_rate_limit_shows_friendly_warning(monkeypatch):
    fake_api(monkeypatch, FakeResponse({}, status_code=429))
    at = AppTest.from_file(APP).run()
    at.chat_input[0].set_value("hi").run()
    assert "very fast" in at.warning[0].value