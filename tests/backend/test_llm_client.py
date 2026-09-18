"""Tests for OpenAILLMClient (app/backend/api/llm_client.py). Per agents/backend.md
("테스트에서 외부 유료 API를 기본 호출하지 않습니다"), no test here ever hits the real
OpenAI network endpoint -- `requests.post` is mocked throughout. This is what closes
the gap flagged in handoffs/DECISIONS.md#D-032's committed follow-ups: "OpenAILLMClient
is an untested stub -- no real external LLM has ever been called."
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from app.backend.api.llm_client import LLMProviderError, OpenAILLMClient, build_llm_client
from app.backend.api.llm_client import MockLLMClient


def _fake_response(content_obj: dict | str, status_ok: bool = True):
    resp = MagicMock()
    resp.raise_for_status = MagicMock() if status_ok else MagicMock(side_effect=requests.HTTPError("500"))
    content = content_obj if isinstance(content_obj, str) else json.dumps(content_obj, ensure_ascii=False)
    resp.json.return_value = {"choices": [{"message": {"content": content}}]}
    return resp


@pytest.fixture()
def context():
    return {
        "evidence": [
            {"evidence_id": "HB-J54-P2", "source_layer": "HISTORY_BASE", "coding_label": "strategic_self_awareness"}
        ],
        "now": "2026-09-19T00:00:00Z",
        "input_refs": {"result_json_run_id": "run-test", "evidence_matrix_checksum": "abc123"},
    }


def test_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        OpenAILLMClient()


def test_model_name_defaults_from_env_var(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("TKAF_LLM_MODEL", "gpt-4.1-mini")
    client = OpenAILLMClient()
    assert client.model_name == "gpt-4.1-mini"


def test_model_name_explicit_arg_overrides_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("TKAF_LLM_MODEL", "gpt-4.1-mini")
    client = OpenAILLMClient(model_name="gpt-4o")
    assert client.model_name == "gpt-4o"


def test_generate_fills_bookkeeping_fields_from_context_not_model(monkeypatch, context):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    client = OpenAILLMClient(model_name="gpt-4o-mini")
    model_payload = {
        # The model is instructed to omit these -- simulate it trying anyway,
        # to prove the caller's values win, not the model's.
        "interpretation_id": "model-supplied-id-should-be-overwritten",
        "generated_at": "2000-01-01T00:00:00Z",
        "status": "ok",
        "coding_validation_notice": "이 근거 코딩은 AI 단독 검증이며, 아직 사람 검증 전 단계입니다.",
        "claims": [
            {
                "claim_id": "c1",
                "claim_type": "observation",
                "text": "정사에서 曹操는 스스로 실수를 인정합니다.",
                "evidence_refs": ["HB-J54-P2"],
                "metric_refs": [],
                "confidence": "high",
            }
        ],
    }
    with patch("app.backend.api.llm_client.requests.post", return_value=_fake_response(model_payload)) as mock_post:
        result = client.generate(event_id="event.chibi", question="曹操는 어떤 인물인가요?", answer_mode="정사", context=context)

    assert mock_post.call_count == 1
    sent = mock_post.call_args.kwargs["json"]
    assert sent["model"] == "gpt-4o-mini"
    assert sent["response_format"] == {"type": "json_object"}
    user_message = json.loads(sent["messages"][1]["content"])
    assert user_message["event_id"] == "event.chibi"
    assert user_message["evidence"][0]["evidence_id"] == "HB-J54-P2"

    # Bookkeeping fields come from context/config, never the model's own output.
    assert result["interpretation_id"] != "model-supplied-id-should-be-overwritten"
    assert result["interpretation_id"].startswith("interp-openai-event.chibi-")
    assert result["generated_at"] == "2026-09-19T00:00:00Z"
    assert result["model"] == {"name": "gpt-4o-mini", "version": "openai-chat-completions"}
    assert result["input_refs"] == {"result_json_run_id": "run-test", "evidence_matrix_checksum": "abc123"}
    # Content fields pass through untouched.
    assert result["status"] == "ok"
    assert result["claims"][0]["evidence_refs"] == ["HB-J54-P2"]
    assert result["prompt_version"] == OpenAILLMClient.PROMPT_VERSION


def test_generate_preserves_model_supplied_prompt_version(monkeypatch, context):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    client = OpenAILLMClient()
    model_payload = {"status": "insufficient_evidence", "abstention_reason": "no data", "claims": [], "prompt_version": "custom_v2"}
    with patch("app.backend.api.llm_client.requests.post", return_value=_fake_response(model_payload)):
        result = client.generate(event_id="event.chibi", question="q", answer_mode="비교", context=context)
    assert result["prompt_version"] == "custom_v2"


def test_generate_raises_llm_provider_error_on_network_failure(monkeypatch, context):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    client = OpenAILLMClient()
    with patch("app.backend.api.llm_client.requests.post", side_effect=requests.exceptions.Timeout("timed out")):
        with pytest.raises(LLMProviderError, match="OpenAI call failed"):
            client.generate(event_id="event.chibi", question="q", answer_mode="비교", context=context)


def test_generate_raises_llm_provider_error_on_http_error_status(monkeypatch, context):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    client = OpenAILLMClient()
    with patch("app.backend.api.llm_client.requests.post", return_value=_fake_response({}, status_ok=False)):
        with pytest.raises(LLMProviderError):
            client.generate(event_id="event.chibi", question="q", answer_mode="비교", context=context)


def test_generate_raises_llm_provider_error_on_malformed_json_content(monkeypatch, context):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    client = OpenAILLMClient()
    with patch("app.backend.api.llm_client.requests.post", return_value=_fake_response("not valid json {{{")):
        with pytest.raises(LLMProviderError):
            client.generate(event_id="event.chibi", question="q", answer_mode="비교", context=context)


def test_generate_raises_llm_provider_error_on_non_object_json_content(monkeypatch, context):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    client = OpenAILLMClient()
    with patch("app.backend.api.llm_client.requests.post", return_value=_fake_response("[1, 2, 3]")):
        with pytest.raises(LLMProviderError, match="not a JSON object"):
            client.generate(event_id="event.chibi", question="q", answer_mode="비교", context=context)


def test_build_llm_client_selects_openai_only_when_provider_and_key_both_set(monkeypatch):
    monkeypatch.setenv("TKAF_LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    assert isinstance(build_llm_client(), OpenAILLMClient)


def test_build_llm_client_falls_back_to_mock_without_key(monkeypatch):
    monkeypatch.setenv("TKAF_LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert isinstance(build_llm_client(), MockLLMClient)


def test_build_llm_client_defaults_to_mock_without_provider_set(monkeypatch):
    monkeypatch.delenv("TKAF_LLM_PROVIDER", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    assert isinstance(build_llm_client(), MockLLMClient)


def test_ask_endpoint_abstains_gracefully_when_provider_call_fails(monkeypatch, fresh_db):
    """Integration check for main.py's LLMProviderError handling: a real provider
    failure (network down, bad key, etc.) must resolve to an honest
    insufficient_evidence response, never an unhandled 500."""
    from app.backend.api.db import DB
    from app.backend.api import main as main_mod
    from fastapi.testclient import TestClient

    class AlwaysFailsClient:
        def generate(self, **kwargs):
            raise LLMProviderError("simulated provider outage")

    monkeypatch.setattr(main_mod, "build_llm_client", lambda: AlwaysFailsClient())
    main_mod.app.state.db = DB(db_path=fresh_db)
    api_client = TestClient(main_mod.app)

    r = api_client.post("/v1/ask", json={"event_id": "event.chibi", "question": "曹操는 어떤 인물인가요?", "answer_mode": "비교"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "insufficient_evidence"
    assert "llm_provider_error" in body["abstention_reason"]
