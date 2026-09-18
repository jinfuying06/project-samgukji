import { useState } from "react";
import { QuestCard, type QuestState } from "../components/QuestCard";
import type { SourceLayer } from "../api/types";

interface Props {
  onOpenEvidence: (id: string) => void;
  onComplete: () => void;
}

/**
 * S-005 Quest — product/user_journeys.md Journey 2 / acceptance_criteria.md AC-5.
 * Fixed to Cao Cao's self-reflection divergence claim (HB-J54-P2 vs RM-C050-P3) for this slice.
 */
export function Quest({ onOpenEvidence, onComplete }: Props) {
  const evidenceLayerById: Record<string, SourceLayer> = {
    "HB-J54-P2": "HISTORY_BASE",
    "RM-C050-P3": "ROMANCE",
  };
  const [seen, setSeen] = useState<string[]>([]);

  const state: QuestState = {
    requiresLayers: ["HISTORY_BASE", "ROMANCE"],
    requiresCounterEvidence: true,
    evidenceSeenIds: seen,
    counterEvidenceIds: ["RM-C050-P3"],
    evidenceLayerById,
  };

  return (
    <div>
      <h1>학습 퀘스트</h1>
      <p className="quest-intro">
        지금 할 일: 曹操에 대한 이야기를 정사(역사책)와 연의(소설) 양쪽에서 하나씩 찾아 읽어보세요. 그리고
        서로 다르게 말하는 근거(반대 근거)도 하나 찾으면, 두 책이 같은 사람을 항상 똑같이 그리지는 않는다는
        걸 직접 확인할 수 있어요!
      </p>
      <QuestCard
        goal="曹操가 적벽대전에서 왜 졌는지, 정사(역사책)와 연의(소설)가 같은 이유를 말하는지 확인하기"
        state={state}
        onOpenEvidence={(id) => {
          setSeen((prev) => (prev.includes(id) ? prev : [...prev, id]));
          onOpenEvidence(id);
        }}
        onComplete={onComplete}
      />
    </div>
  );
}
