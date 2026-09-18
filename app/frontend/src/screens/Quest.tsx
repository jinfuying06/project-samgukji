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

  const layersSatisfied = state.requiresLayers.every((l) =>
    seen.some((id) => evidenceLayerById[id] === l)
  );
  const counterSatisfied = state.counterEvidenceIds.some((id) => seen.includes(id));

  return (
    <div>
      <QuestCard
        goal="曹操가 왜 졌는지, 정사와 연의가 같은 이유를 대는지 확인하기"
        state={state}
        onOpenEvidence={(id) => {
          setSeen((prev) => (prev.includes(id) ? prev : [...prev, id]));
          onOpenEvidence(id);
        }}
      />
      {layersSatisfied && counterSatisfied && (
        <button type="button" onClick={onComplete} className="quest-continue-btn">
          퀴즈로 이동
        </button>
      )}
    </div>
  );
}
