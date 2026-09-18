"""LLM client interface, per analysis/llm_contract.md and app/architecture/system.md.

Provider/model is configurable via env var, never hardcoded (system.md's
"Required decisions"). Tests never call a real paid API (agents/backend.md
prohibition) -- they use MockLLMClient exclusively. main.py falls back to
MockLLMClient automatically when no API key is configured, so the app runs
end-to-end without any external dependency.
"""
from __future__ import annotations

import abc
import os


class LLMClient(abc.ABC):
    @abc.abstractmethod
    def generate(self, *, event_id: str, question: str, answer_mode: str, context: dict) -> dict:
        """Returns a RAW candidate payload shaped like
        analysis/schemas/interpretation.schema.json. Not guaranteed valid --
        the caller (main.py's llm_validator) must validate it before use."""
        raise NotImplementedError


class OpenAILLMClient(LLMClient):
    """Real provider client. Not exercised by tests (no paid API calls in
    tests, per agents/backend.md). Prompt construction must use only
    already-short, already-public-domain-confirmed excerpts from the DB
    (context['evidence']), never raw/private-analysis text
    (app/architecture/threat_model.md)."""

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.model_name = model_name
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set; use MockLLMClient instead")

    def generate(self, *, event_id: str, question: str, answer_mode: str, context: dict) -> dict:  # pragma: no cover
        raise NotImplementedError(
            "Real OpenAI call not implemented in this slice -- no network access in this "
            "environment and tests must not hit a paid API. Wire this up when a key and "
            "an approved provider are actually available; keep the interface unchanged."
        )


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
