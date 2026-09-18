import { useState } from "react";
import type { EvidenceSpan } from "../api/types";

const LAYER_LABEL: Record<string, string> = {
  HISTORY_BASE: "정사",
  HISTORY_ANNOTATION: "정사 주석",
  ROMANCE: "연의",
  LATER_INTERPRETATION: "연구·해석",
  GAME_DATA: "게임",
};

interface Props {
  evidence: EvidenceSpan;
  personName?: string;
}

/**
 * design/component_spec.md `EvidenceCard`. Always renders the D-017 coding-validation
 * disclosure — never hideable — and never renders "no data" the same as a populated card.
 */
export function EvidenceCard({ evidence, personName }: Props) {
  const [expanded, setExpanded] = useState(false);
  const accessibleName = `${personName ?? ""} 근거, ${evidence.work_title} ${evidence.volume_or_chapter}, ${
    LAYER_LABEL[evidence.source_layer]
  }`.trim();

  return (
    <article
      className={`evidence-card layer-${evidence.source_layer}`}
      aria-label={accessibleName}
      data-testid="evidence-card"
    >
      <div className="evidence-card-head">
        <span className={`badge layer-${evidence.source_layer}`}>{LAYER_LABEL[evidence.source_layer]}</span>
        <span className="evidence-id mono">{evidence.evidence_id}</span>
      </div>
      <p className="evidence-locator">
        {evidence.work_title} · {evidence.volume_or_chapter}
      </p>
      {evidence.permitted_excerpt && <blockquote className="evidence-excerpt">{evidence.permitted_excerpt}</blockquote>}
      <p className="evidence-label mono">{evidence.coding_label}</p>

      {evidence.ambiguity_note && (
        <p className="evidence-ambiguity" aria-describedby={`${evidence.evidence_id}-ambiguity`}>
          <span id={`${evidence.evidence_id}-ambiguity`}>{evidence.ambiguity_note}</span>
        </p>
      )}

      {/* D-017 disclosure — mandatory, never suppressible */}
      <p className="coding-validation-notice" role="note">
        {evidence.coding_validation_status === "human_validated"
          ? "사람 검증 완료"
          : "⚠ AI 단독 검증만 완료 (사람 검증 전, D-017)"}
      </p>

      <button
        type="button"
        aria-expanded={expanded}
        onClick={() => setExpanded((v) => !v)}
        className="evidence-expand-btn"
      >
        {expanded ? "간략히 보기" : "자세히 보기"}
      </button>
      {expanded && (
        <dl className="evidence-detail">
          <dt>Confidence</dt>
          <dd>{evidence.confidence.toFixed(2)}</dd>
          <dt>검토 상태</dt>
          <dd>{evidence.review_status}</dd>
          {evidence.edition_ref && (
            <>
              <dt>판본</dt>
              <dd>{evidence.edition_ref}</dd>
            </>
          )}
        </dl>
      )}
    </article>
  );
}

/** design/wireframe_brief.md AC-2: missing-layer state must render as an explicit card, not blank space. */
export function EvidenceCardEmpty({ layerLabel }: { layerLabel: string }) {
  return (
    <div className="evidence-card evidence-card-empty" role="status">
      이 층위({layerLabel})에서는 근거 없음
    </div>
  );
}
