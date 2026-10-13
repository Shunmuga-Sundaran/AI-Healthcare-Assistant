
from types import SimpleNamespace

import pytest
from google.genai import errors as genai_errors

from modules import gemini_service as gs


class FakeModels:
    def __init__(self, response=None, error=None):
        self.response, self.error, self.kwargs = response, error, None

    def generate_content(self, **kwargs):
        self.kwargs = kwargs
        if self.error:
            raise self.error
        return self.response


def fake_client(response=None, error=None):
    return SimpleNamespace(models=FakeModels(response, error))


def api_error(code):
    return genai_errors.APIError(code, {"error": {"message": "x", "status": "X"}})


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(gs.GeminiServiceError, match="API key is missing"):
        gs.generate_guidance("mild headache")


def test_placeholder_key_counts_as_missing(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "your_api_key_here")
    assert gs.get_api_key() is None


def test_success_returns_text():
    client = fake_client(SimpleNamespace(text="  Some guidance  "))
    assert gs.generate_guidance("mild headache", ["headache"], client=client) == "Some guidance"
    sent = client.models.kwargs
    assert "mild headache" in sent["contents"]
    assert "diagnosis" in sent["config"].system_instruction.lower()


def test_empty_response_is_error():
    with pytest.raises(gs.GeminiServiceError, match="no text"):
        gs.generate_guidance("mild headache", client=fake_client(SimpleNamespace(text="")))


@pytest.mark.parametrize("code,fragment", [
    (401, "key was rejected"),
    (403, "key was rejected"),
    (404, "not found"),
    (429, "quota"),
    (503, "temporarily unavailable"),
])
def test_api_errors_are_translated(code, fragment):
    with pytest.raises(gs.GeminiServiceError, match=fragment):
        gs.generate_guidance("mild headache", client=fake_client(error=api_error(code)))


def test_timeout_is_translated():
    class ReadTimeout(Exception):
        pass

    with pytest.raises(gs.GeminiServiceError, match="timed out"):
        gs.generate_guidance("mild headache", client=fake_client(error=ReadTimeout("slow")))


def test_network_error_is_translated():
    with pytest.raises(gs.GeminiServiceError, match="Could not reach"):
        gs.generate_guidance("mild headache", client=fake_client(error=ConnectionError("down")))


def test_prompt_contains_keywords():
    assert "fever" in gs.build_prompt("fever and cough", ["fever"])
