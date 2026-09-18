import { useState } from "react";
import type { AnswerMode, Interpretation } from "../api/types";

interface Props {
  answerMode: AnswerMode;
  onAsk: (question: string, mode: AnswerMode) => void;
  result: Interpretation | null;
  loading?: boolean;
  error?: boolean;
  onEvidenceClick?: (evidenceId: string) => void;
}

const MODES: AnswerMode[] = ["정사", "연의", "비교", "게임"];

/**
 * design/component_spec.md `AIAnswerPanel`, schema: analysis/schemas/interpretation.schema.json.
 * Abstained claims are announced distinctly; 연의-mode answers are visually marked as literary.
 */
export function AIAnswerPanel({ answerMode, onAsk, result, loading, error, onEvidenceClick }: Props) {
  const [question, setQuestion] = useState("");
  const [mode, setMode] = useState<AnswerMode>(answerMode);

  return (
    <section className="ai-answer-panel" role="region" aria-label="AI 답변 패널">
      <h1>AI에게 물어보기</h1>
      <div role="radiogroup" aria-label="답변 모드">
        {MODES.map((m) => (
          <button
            key={m}
            type="button"
            role="radio"
            aria-checked={mode === m}
            className={mode === m ? "selected" : ""}
            onClick={() => setMode(m)}
          >
            {m}
          </button>
        ))}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (question.trim()) onAsk(question.trim(), mode);
        }}
      >
        <label htmlFor="ai-question-input">질문</label>
        <input
          id="ai-question-input"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="예: 曹操는 적벽대전 패배 후 어떻게 반응했나요?"
        />
        <button type="submit">질문하기</button>
      </form>

      {loading && (
        <p role="status" aria-live="polite">
          답변 생성 중…
        </p>
      )}

      {error && (
        <p role="alert" className="ai-answer-error">
          AI 서비스에 연결할 수 없습니다. <button type="button">재시도</button>
        </p>
      )}

      {!loading && !error && result && result.status !== "ok" && (
        <div role="status" aria-live="polite" className="ai-answer-abstained">
          <p>{mode === "연의" ? "(연의 답변은 문학적 서술이며 역사적 사실이 아닙니다)" : null}</p>
          <p>답변을 보류합니다: {result.abstention_reason}</p>
        </div>
      )}

      {!loading && !error && result && result.status === "ok" && (
        <div className="ai-answer-claims">
          {mode === "연의" && <p className="ai-answer-fiction-flag">⚠ 연의(문학) 서술 — 역사적 사실이 아님</p>}
          {result.claims.map((claim) => (
            <div key={claim.claim_id} className={`ai-answer-claim claim-${claim.claim_type}`}>
              <p>{claim.text}</p>
              <div className="ai-answer-evidence-chips">
                {claim.evidence_refs.map((id) => (
                  <button key={id} type="button" className="evidence-chip" onClick={() => onEvidenceClick?.(id)}>
                    {id}
                  </button>
                ))}
                {claim.metric_refs.map((id) => (
                  <span key={id} className="metric-chip">
                    {id}
                  </span>
                ))}
              </div>
              {claim.caveats?.map((c, i) => (
                <p key={i} className="ai-answer-caveat">
                  {c}
                </p>
              ))}
            </div>
          ))}
          {result.coding_validation_notice && (
            <p className="coding-validation-notice" role="note">
              {result.coding_validation_notice}
            </p>
          )}
        </div>
      )}
    </section>
  );
}
