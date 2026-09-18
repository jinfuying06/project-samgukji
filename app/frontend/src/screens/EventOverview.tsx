import { useEffect, useState } from "react";
import { api, ApiError } from "../api/client";
import type { PeopleResponse, SourceLayer } from "../api/types";
import { SourceModeControl, type SourceModeOption, type SourceModeValue } from "../components/SourceModeControl";

const ALL_LAYERS: SourceLayer[] = ["HISTORY_BASE", "HISTORY_ANNOTATION", "ROMANCE"];

interface Props {
  eventId: string;
  onSelectPerson: (personId: string) => void;
  onStartQuest: () => void;
}

/** S-001 Event overview — see design/wireframe_brief.md. */
export function EventOverview({ eventId, onSelectPerson, onStartQuest }: Props) {
  const [data, setData] = useState<PeopleResponse | null>(null);
  const [status, setStatus] = useState<"loading" | "ok" | "empty" | "error">("loading");
  const [mode, setMode] = useState<SourceModeValue>("비교");

  useEffect(() => {
    let cancelled = false;
    setStatus("loading");
    api
      .getPeople(eventId)
      .then((res) => {
        if (cancelled) return;
        setData(res);
        setStatus(res.people.length === 0 ? "empty" : "ok");
      })
      .catch(() => !cancelled && setStatus("error"));
    return () => {
      cancelled = true;
    };
  }, [eventId]);

  if (status === "loading") {
    return (
      <div role="status" aria-label="사건 데이터 로딩 중">
        불러오는 중…
      </div>
    );
  }
  if (status === "error") {
    return (
      <div role="alert">
        표시할 사건 데이터를 불러오지 못했습니다. <button type="button">재시도</button>
      </div>
    );
  }
  if (status === "empty" || !data) {
    return <div role="status">표시할 사건 데이터 없음</div>;
  }

  const options: SourceModeOption[] = [
    ...ALL_LAYERS.map((l) => ({ value: l as SourceModeValue })),
    { value: "비교" },
  ];

  const layerLabel: Partial<Record<SourceLayer, string>> = {
    HISTORY_BASE: "정사",
    HISTORY_ANNOTATION: "정사 주석",
    ROMANCE: "연의",
  };

  return (
    <section aria-label="적벽대전 사건 개요" className="event-overview">
      <div className="event-hero">
        <h1>적벽대전 <span className="event-hero-en">(Battle of Red Cliffs)</span></h1>
        <p className="event-scope-note">
          이 슬라이스는 적벽대전 一개 사건, <strong>{data.people.length}명</strong> 한정입니다. 더 많은 인물 추가 예정 (D-016).
        </p>
      </div>
      <SourceModeControl options={options} value={mode} onChange={setMode} />
      <div className="person-grid-head" aria-hidden="true">
        <span className="person-grid-head-name">인물</span>
        {ALL_LAYERS.map((l) => (
          <span key={l} className={`person-grid-head-layer layer-${l}`}>
            {layerLabel[l]}
          </span>
        ))}
      </div>
      <ul className="person-list">
        {data.people.map((p) => (
          <li key={p.person_id} className="person-row">
            <button type="button" className="person-pill" onClick={() => onSelectPerson(p.person_id)}>
              {p.canonical_name_zh}
            </button>
            <span className="person-coverage-badges">
              {ALL_LAYERS.map((l) => {
                const count = p.evidence_coverage[l] ?? 0;
                return (
                  <span
                    key={l}
                    className={`coverage-badge layer-${l}${count === 0 ? " coverage-badge-empty" : ""}`}
                  >
                    {count > 0 ? count : "근거 없음"}
                  </span>
                );
              })}
            </span>
          </li>
        ))}
      </ul>
      <button type="button" onClick={onStartQuest} className="start-quest-btn">
        학습 시작 →
      </button>
    </section>
  );
}
