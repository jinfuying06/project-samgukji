"""LLM client interface, per analysis/llm_contract.md and app/architecture/system.md.

Provider/model is configurable via env var, never hardcoded (system.md's
"Required decisions"). Tests never call a real paid API (agents/backend.md
prohibition) -- they use MockLLMClient exclusively, and OpenAILLMClient's own
tests mock `requests.post` (tests/backend/test_llm_client.py). main.py falls
back to MockLLMClient automatically when no API key is configured, so the app
runs end-to-end without any external dependency.
"""
from __future__ import annotations

import abc
import json
import os

import requests

from .llm_validator import load_interpretation_schema


class LLMClient(abc.ABC):
    @abc.abstractmethod
    def generate(self, *, event_id: str, question: str, answer_mode: str, context: dict) -> dict:
        """Returns a RAW candidate payload shaped like
        analysis/schemas/interpretation.schema.json. Not guaranteed valid --
        the caller (main.py's llm_validator) must validate it before use."""
        raise NotImplementedError


class LLMProviderError(RuntimeError):
    """The provider call itself failed (network/timeout/malformed response) --
    distinct from InterpretationValidationError, which means the call
    succeeded but the payload failed schema/citation checks. main.py treats
    both the same way: consume one retry attempt, then abstain -- it never
    lets a provider failure surface as a raw 500."""


class OpenAILLMClient(LLMClient):
    """Real provider client (OpenAI-compatible Chat Completions API).

    Prompt construction uses only already-short, already-public-domain-confirmed
    excerpts the caller already filtered by answer_mode's allowed source layers
    (context['evidence'], populated by main.py's /v1/ask handler from the
    curated DB) -- never raw/private-analysis text (app/architecture/threat_model.md).

    The model is asked to produce only the *content* fields (status, claims,
    abstention_reason, coding_validation_notice, prompt_version). Bookkeeping
    fields the model could get wrong or hallucinate (interpretation_id,
    generated_at, model, input_refs) are filled in here from context/config
    instead of trusted from the model's own output -- consistent with this
    project's "code computes, LLM explains" rule (handoffs/DECISIONS.md#D-002).

    Not exercised by the default test suite (no paid API calls in tests, per
    agents/backend.md) -- tests/backend/test_llm_client.py covers prompt
    construction, response parsing, and error handling entirely by mocking
    `requests.post`, no network access required.
    """

    API_URL = "https://api.openai.com/v1/chat/completions"
    PROMPT_VERSION = "openai_v1_llm_contract_v1"
    TIMEOUT_SECONDS = 30

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or os.environ.get("TKAF_LLM_MODEL", "gpt-4o-mini")
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set; use MockLLMClient instead")

    def _build_messages(self, *, event_id: str, question: str, answer_mode: str, context: dict) -> list[dict]:
        schema = load_interpretation_schema()
        evidence = context.get("evidence", [])
        system = (
            "You are the TKAF LLM Analyst for the 적벽대전 (Battle of Red Cliffs) vertical slice. "
            "Follow analysis/llm_contract.md exactly. Respond with a single JSON object only -- "
            "no prose outside the JSON, no markdown code fences.\n\n"
            "The 'evidence' list below has already been filtered to the source layer(s) allowed "
            f"for answer_mode '{answer_mode}' -- do not reference any source layer not present in it.\n\n"
            "Rules:\n"
            "1. Every claim needs >=1 evidence_refs (an evidence_id that literally appears in the "
            "'evidence' list below) or >=1 metric_refs -- never neither, and never an evidence_id "
            "you invented.\n"
            "2. Do not mix HISTORY_BASE/HISTORY_ANNOTATION/ROMANCE content into a single claim's "
            "text -- keep each source layer's claims separate.\n"
            "3. If any claim's evidence_refs is non-empty, you MUST also set the top-level field "
            "'coding_validation_notice' disclosing that this evidence coding is LLM-LLM validated "
            "only (Cohen's kappa=0.90), not human-validated (handoffs/DECISIONS.md#D-017).\n"
            "4. If the 'evidence' list below is empty, or the question asks for a score/ranking/"
            "centrality value that does not exist in this slice, set status='insufficient_evidence' "
            "with a specific abstention_reason naming what's missing, and emit no claims.\n"
            "5. Never invent a score, ranking, or centrality metric not present in 'evidence'. Never "
            "give personalized life advice or a moral/character diagnosis about a historical figure.\n"
            "6. Only output 'status', 'claims', 'abstention_reason' (if applicable), "
            "'coding_validation_notice' (if applicable), and 'prompt_version' -- omit "
            "interpretation_id/generated_at/model/input_refs, the caller fills those in.\n\n"
            "JSON schema your output must satisfy for the fields listed in rule 6 (other required "
            f"top-level fields are filled in by the caller, not you): {json.dumps(schema, ensure_ascii=False)}"
        )
        user = json.dumps(
            {"event_id": event_id, "question": question, "answer_mode": answer_mode, "evidence": evidence},
            ensure_ascii=False,
        )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

    def generate(self, *, event_id: str, question: str, answer_mode: str, context: dict) -> dict:
        messages = self._build_messages(event_id=event_id, question=question, answer_mode=answer_mode, context=context)
        try:
            response = requests.post(
                self.API_URL,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model_name,
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"},
                    "messages": messages,
                },
                timeout=self.TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as exc:
            raise LLMProviderError(f"OpenAI call failed: {exc}") from exc

        if not isinstance(parsed, dict):
            raise LLMProviderError(f"OpenAI response content was not a JSON object: {content!r}")

        parsed["interpretation_id"] = f"interp-openai-{event_id}-{abs(hash(question)) % 100000}"
        parsed["generated_at"] = context.get("now", "1970-01-01T00:00:00Z")
        parsed["model"] = {"name": self.model_name, "version": "openai-chat-completions"}
        parsed["input_refs"] = context.get("input_refs", {})
        parsed.setdefault("prompt_version", self.PROMPT_VERSION)
        return parsed


class MockLLMClient(LLMClient):
    """Deterministic stand-in used by default (no API key configured) and by
    all automated tests. Builds a schema-shaped response directly from the
    real evidence/metrics passed in `context` -- it does not invent content,
    it restates what's already in the DB, which is exactly what a correctly
    behaving real LLM is contracted to do (analysis/llm_contract.md rule 2)."""

    def generate(self, *, event_id: str, question: str, answer_mode: str, context: dict) -> dict:
        if question.strip() == "FORCE_INVALID_FOR_TEST":
            # Deliberately malformed (missing required 'confidence') so tests
            # can exercise the retry-then-abstain path in main.py.
            return {
                "interpretation_id": "interp-test-invalid",
                "answer_mode": answer_mode,
                "status": "ok",
                "generated_at": "2026-09-18T00:00:00Z",
                "model": {"name": "mock", "version": "test"},
                "prompt_version": "mock_v1",
                "input_refs": context.get("input_refs", {}),
                "claims": [
                    {
                        "claim_id": "c1",
                        "claim_type": "observation",
                        "text": "intentionally malformed for a validator test",
                        "evidence_refs": [],
                        "metric_refs": [],
                        # 'confidence' omitted on purpose
                    }
                ],
            }

        evidence = context.get("evidence", [])
        now = context.get("now", "2026-09-18T00:00:00Z")
        base = {
            "interpretation_id": f"interp-mock-{event_id}-{abs(hash(question)) % 100000}",
            "answer_mode": answer_mode,
            "generated_at": now,
            "model": {"name": "mock", "version": "1.0.0"},
            "prompt_version": "mock_v1",
            "input_refs": context.get("input_refs", {}),
        }

        if not evidence:
            base.update(
                {
                    "status": "insufficient_evidence",
                    "abstention_reason": f"이 이벤트/모드({answer_mode})에 해당하는 근거가 이 슬라이스에 아직 없습니다.",
                    "claims": [],
                }
            )
            return base

        top = evidence[0]
        base.update(
            {
                "status": "ok",
                "coding_validation_notice": (
                    "이 근거 코딩은 AI 단독 검증(2차 AI 코더와의 일치도 Cohen's kappa=0.90)이며, "
                    "아직 사람 검증 전 단계입니다. (handoffs/DECISIONS.md#D-017)"
                ),
                "claims": [
                    {
                        "claim_id": "c1",
                        "claim_type": "observation",
                        "text": f"{top['coding_label']} 라벨이 붙은 근거({top['evidence_id']})가 이 질문과 관련이 있습니다.",
                        "evidence_refs": [top["evidence_id"]],
                        "metric_refs": [],
                        "confidence": "medium",
                    }
                ],
            }
        )
        return base


def build_llm_client() -> LLMClient:
    provider = os.environ.get("TKAF_LLM_PROVIDER", "mock").lower()
    if provider == "openai" and os.environ.get("OPENAI_API_KEY"):
        return OpenAILLMClient()
    return MockLLMClient()
