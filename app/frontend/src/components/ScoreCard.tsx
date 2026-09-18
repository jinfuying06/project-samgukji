import type { Metric, ScoreType } from "../api/types";

interface Props {
  metric: Metric | null;
  scoreType: ScoreType;
  loading?: boolean;
  error?: boolean;
}

function parseDivergence(method?: string): { classification: string; evidenceIds: string[] } | null {
  if (!method) return null;
  const m = method.match(/classification=(\w+); evidence_ids=([^;]+)/);
  if (!m) return null;
  return { classification: m[1], evidenceIds: m[2].split(",") };
}

/**
 * design/component_spec.md `ScoreCard`. This slice has NO composite score
 * (analysis/scoring_model.md stops before the display-score stage) — the default
 * state is `insufficient_data`, rendering coverage/label_frequency/divergence instead
 * of a fabricated number. Never renders a 0 count the same way as a populated card.
 */
export function ScoreCard({ metric, scoreType, loading, error }: Props) {
  if (loading) {
    return (
      <div className="score-card score-card-loading" role="status" aria-label="점수 카드 로딩 중">
        불러오는 중…
      </div>
    );
  }
  if (error) {
    return (
      <div className="score-card score-card-error" role="alert">
        불러오지 못했습니다. <button type="button">재시도</button>
      </div>
    );
  }
  if (scoreType === "insufficient_data" || !metric) {
    return (
      <div className="score-card score-card-insufficient" role="status">
        <p className="score-type-badge insufficient_data">데이터 부족</p>
        <p>아직 합성 점수 없음 — 이 슬라이스는 근거 커버리지·라벨 빈도·발산 분류만 제공합니다.</p>
      </div>
    );
  }

  const divergence = metric.unit === "categorical_classification" ? parseDivergence(metric.method) : null;
  const isCount = metric.unit === "evidence_span_count" || metric.unit === "edge_count";
  const accessibleName = `${metric.name}: ${
    divergence ? divergence.classification : metric.value === null ? "값 없음" : `${metric.value}${isCount ? "건" : ""}`
  }`;

  return (
    <div
      className={`score-card score-type-${scoreType}`}
      role="group"
      aria-label={accessibleName}
      data-testid="score-card"
    >
      <p className={`score-type-badge ${scoreType}`}>
        {scoreType === "default" && "기본 지표"}
        {scoreType === "user_custom" && "사용자 설정 점수"}
        {scoreType === "external_game" && "외부 게임 수치"}
      </p>
      <p className="score-card-name">{metric.name}</p>
      {divergence ? (
        <p className={`divergence-badge divergence-${divergence.classification}`}>{divergence.classification}</p>
      ) : metric.value === null ? (
        <p className="score-card-value-unavailable">측정 불가</p>
      ) : (
        <p className="score-card-value">
          {metric.value}
          <span className="score-card-unit"> {metric.unit === "evidence_span_count" ? "건" : metric.unit}</span>
        </p>
      )}
    </div>
  );
}
