import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Metric, MetricsResponse, PersonWithCoverage } from "../api/types";
import { ScoreCard } from "../components/ScoreCard";
import { ContributionBreakdown } from "../components/ContributionBreakdown";

interface Props {
  eventId: string;
  personId?: string;
}

/** S-003 Score breakdown & weight lab — this slice has no composite score, see design/wireframe_brief.md. */
export function ScoreBreakdown({ eventId, personId }: Props) {
  const [data, setData] = useState<MetricsResponse | null>(null);
  const [status, setStatus] = useState<"loading" | "ok" | "empty" | "error">("loading");
  const [people, setPeople] = useState<PersonWithCoverage[] | null>(null);
  const [selectedPersonId, setSelectedPersonId] = useState<string | undefined>(personId);
  const [weightLabOpen, setWeightLabOpen] = useState(false);

  useEffect(() => {
    api.getPeople(eventId).then((res) => setPeople(res.people)).catch(() => setPeople([]));
  }, [eventId]);

  useEffect(() => {
    let cancelled = false;
    setStatus("loading");
    api
      .getMetrics(eventId)
      .then((res) => {
        if (cancelled) return;
        setData(res);
        setStatus(res.metrics.length === 0 ? "empty" : "ok");
      })
      .catch(() => !cancelled && setStatus("error"));
    return () => {
      cancelled = true;
    };
  }, [eventId]);

  if (status === "loading") return <div role="status">불러오는 중…</div>;
  if (status === "error")
    return (
      <div role="alert">
        불러오지 못했습니다. <button type="button">재시도</button>
      </div>
    );
  if (status === "empty" || !data) return <div role="status">표시할 관측 데이터 없음</div>;

  const relevant: Metric[] = personId
    ? data.metrics.filter((m) => m.metric_id.includes(personId.split(".")[1]?.toUpperCase() ?? "@@none@@"))
    : data.metrics;
  const shown = relevant.length ? relevant : data.metrics;

  const divergence = shown.filter((m) => m.metric_id.startsWith("divergence."));
  const coverage = shown.filter((m) => m.metric_id.startsWith("coverage."));
  const labelFreq = shown.filter((m) => m.metric_id.startsWith("label_frequency."));
  const other = shown.filter(
    (m) => !m.metric_id.startsWith("divergence.") && !m.metric_id.startsWith("coverage.") && !m.metric_id.startsWith("label_frequency.")
  );

  return (
    <section aria-label="점수 분해 및 가중치 실험실">
      <h2>근거 → 코드 → … → 점수</h2>
      <p className="population-note">
        표본 크기 n={data.population.n}. {data.population.description}
      </p>

      <ScoreCard metric={null} scoreType="insufficient_data" />

      <button
        type="button"
        className="weight-lab-btn"
        aria-expanded={weightLabOpen}
        onClick={() => setWeightLabOpen((v) => !v)}
      >
        {weightLabOpen ? "가중치 실험 닫기" : "가중치 실험 열기 (정사 vs 연의, 어디에 무게를 둘까?)"}
      </button>

      {weightLabOpen && (
        <div className="weight-lab-person-picker">
          <label htmlFor="weight-lab-person-select">인물 선택</label>
          <select
            id="weight-lab-person-select"
            value={selectedPersonId ?? ""}
            onChange={(e) => setSelectedPersonId(e.target.value || undefined)}
          >
            <option value="">-- 인물을 선택하세요 --</option>
            {(people ?? []).map((p) => (
              <option key={p.person_id} value={p.person_id}>
                {p.canonical_name_zh}
              </option>
            ))}
          </select>
          <ContributionBreakdown
            personId={selectedPersonId}
            personName={people?.find((p) => p.person_id === selectedPersonId)?.canonical_name_zh}
          />
        </div>
      )}

      {divergence.length > 0 && (
        <div className="metrics-section">
          <h3>정사·연의 발산 사례 ({divergence.length})</h3>
          <div className="metrics-grid metrics-grid-wide">
            {divergence.map((m) => (
              <ScoreCard key={m.metric_id} metric={m} scoreType="default" />
            ))}
          </div>
        </div>
      )}

      {coverage.length > 0 && (
        <div className="metrics-section">
          <h3>인물×출처층위 근거 커버리지 ({coverage.length})</h3>
          <div className="metrics-grid metrics-grid-compact">
            {coverage.map((m) => (
              <ScoreCard key={m.metric_id} metric={m} scoreType="default" />
            ))}
          </div>
        </div>
      )}

      {labelFreq.length > 0 && (
        <div className="metrics-section">
          <h3>코딩 라벨 빈도 ({labelFreq.length})</h3>
          <ul className="label-freq-chips">
            {labelFreq.map((m) => (
              <li key={m.metric_id} className="label-freq-chip">
                <span className="label-freq-name">{m.name.replace("Coding-label frequency: ", "")}</span>
                <span className="label-freq-count">{m.value}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {other.length > 0 && (
        <div className="metrics-section">
          <h3>기타 지표 ({other.length})</h3>
          <div className="metrics-grid metrics-grid-compact">
            {other.map((m) => (
              <ScoreCard key={m.metric_id} metric={m} scoreType="default" />
            ))}
          </div>
        </div>
      )}

      <ul className="limitations-list">
        {data.limitations.map((l, i) => (
          <li key={i}>{l}</li>
        ))}
      </ul>
    </section>
  );
}
