import { useState } from "react";
import { api, ApiError } from "../api/client";
import type { AnswerMode, Interpretation } from "../api/types";
import { AIAnswerPanel } from "../components/AIAnswerPanel";

interface Props {
  eventId: string;
  onEvidenceClick?: (evidenceId: string) => void;
}

/** S-004 AI answer panel screen. */
export function AskAI({ eventId, onEvidenceClick }: Props) {
  const [result, setResult] = useState<Interpretation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const handleAsk = (question: string, mode: AnswerMode) => {
    setLoading(true);
    setError(false);
    api
      .ask({ event_id: eventId, question, answer_mode: mode })
      .then((res) => setResult(res))
      .catch((e) => {
        // 503/service failure is distinct from a valid insufficient_evidence 200 response.
        if (e instanceof ApiError && e.status === 503) setError(true);
        else setError(true);
      })
      .finally(() => setLoading(false));
  };

  return (
    <AIAnswerPanel
      answerMode="비교"
      onAsk={handleAsk}
      result={result}
      loading={loading}
      error={error}
      onEvidenceClick={onEvidenceClick}
    />
  );
}
