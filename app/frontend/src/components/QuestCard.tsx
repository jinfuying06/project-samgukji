import { useMemo } from "react";
import type { SourceLayer } from "../api/types";

export interface QuestState {
  requiresLayers: SourceLayer[];
  requiresCounterEvidence: boolean;
  evidenceSeenIds: string[];
  counterEvidenceIds: string[];
  /** map of evidence_id -> source_layer, for gate computation */
  evidenceLayerById: Record<string, SourceLayer>;
}

interface Props {
  goal: string;
  state: QuestState;
  onOpenEvidence: (id: string) => void;
}

/**
 * design/component_spec.md `QuestCard` + product/acceptance_criteria.md AC-5:
 * completion is gated on real state, never a single click. "완료" stays present but
 * aria-disabled (not removed from the DOM) until both gates are satisfied.
 */
export function QuestCard({ goal, state, onOpenEvidence }: Props) {
  const { requiresLayers, requiresCounterEvidence, evidenceSeenIds, counterEvidenceIds, evidenceLayerById } = state;

  const seenLayers = useMemo(
    () => new Set(evidenceSeenIds.map((id) => evidenceLayerById[id]).filter(Boolean)),
    [evidenceSeenIds, evidenceLayerById]
  );
  const layersSatisfied = requiresLayers.every((l) => seenLayers.has(l));
  const counterEvidenceSatisfied =
    !requiresCounterEvidence || counterEvidenceIds.some((id) => evidenceSeenIds.includes(id));
  const canComplete = layersSatisfied && counterEvidenceSatisfied;

  const missingLayers = requiresLayers.filter((l) => !seenLayers.has(l));
  const unmetGateText = !layersSatisfied
    ? `아직 확인하지 않은 출처: ${missingLayers.join(", ")}`
    : !counterEvidenceSatisfied
    ? "반대 근거를 아직 확인하지 않았습니다"
    : "";

  return (
    <section className="quest-card" role="region" aria-label={`퀘스트: ${goal}`}>
      <h3>{goal}</h3>
      <p aria-live="polite" className="quest-progress">
        {evidenceSeenIds.length}/{requiresLayers.length + (requiresCounterEvidence ? 1 : 0)} 근거 확인, 반대 근거{" "}
        {counterEvidenceSatisfied ? "확인됨" : "미확인"}
      </p>
      {!canComplete && (
        <p className="quest-gate-reason" role="status">
          {unmetGateText}
        </p>
      )}
      <ul className="quest-evidence-list">
        {counterEvidenceIds.map((id) => (
          <li key={id}>
            <button type="button" onClick={() => onOpenEvidence(id)}>
              {evidenceSeenIds.includes(id) ? "✓ " : ""}근거 {id}
              {counterEvidenceIds.includes(id) ? " (반대 근거)" : ""}
            </button>
          </li>
        ))}
      </ul>
      <button type="button" aria-disabled={!canComplete} disabled={false} className="quest-complete-btn"
        onClick={(e) => {
          if (!canComplete) e.preventDefault();
        }}
      >
        완료
      </button>
    </section>
  );
}
