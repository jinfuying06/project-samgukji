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
          지금은 적벽대전 이야기 속 인물 <strong>{data.people.length}명</strong>만 볼 수 있어요. 나중에 더 많은 사람이 추가될
          예정이에요.
        </p>
        <p className="event-evidence-intro">
          아래 표의 숫자는 그 사람에 대해 정사(진짜 역사책)나 연의(재미있게 쓴 소설)에 실제로 적힌 문장이 몇 개
          있는지 세어놓은 거예요. 숫자가 많다고 그 사람이 더 대단한 건 아니에요 — 그 책에 그 사람 이야기가 더
          많이 적혀 있었다는 뜻일 뿐이에요. "근거 없음"이라고 나오면 그건 "0점"이 아니라, 아직 찾아낸 기록이
          없다는 뜻이에요.
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
