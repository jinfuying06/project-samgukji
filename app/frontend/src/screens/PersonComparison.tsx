import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { EvidenceSpan, SourceLayer } from "../api/types";
import { EvidenceCard, EvidenceCardEmpty } from "../components/EvidenceCard";
import { SourceModeControl, type SourceModeOption, type SourceModeValue } from "../components/SourceModeControl";

const LAYERS: SourceLayer[] = ["HISTORY_BASE", "HISTORY_ANNOTATION", "ROMANCE"];
const LAYER_LABEL: Record<SourceLayer, string> = {
  HISTORY_BASE: "정사",
  HISTORY_ANNOTATION: "정사 주석",
  ROMANCE: "연의",
  LATER_INTERPRETATION: "연구·해석",
  GAME_DATA: "게임",
};

interface Props {
  personId: string;
  personName: string;
  onAskAI: (personId: string) => void;
}

/** S-002 Person comparison — see design/wireframe_brief.md. */
export function PersonComparison({ personId, personName, onAskAI }: Props) {
  const [evidence, setEvidence] = useState<EvidenceSpan[] | null>(null);
  const [status, setStatus] = useState<"loading" | "ok" | "empty" | "error">("loading");
  const [mode, setMode] = useState<SourceModeValue>("비교");

  useEffect(() => {
    let cancelled = false;
    setStatus("loading");
    api
      .getEvidence(personId)
      .then((res) => {
        if (cancelled) return;
        setEvidence(res.evidence);
        setStatus(res.evidence.length === 0 ? "empty" : "ok");
      })
      .catch(() => !cancelled && setStatus("error"));
    return () => {
      cancelled = true;
    };
  }, [personId]);

  if (status === "loading") return <div role="status">불러오는 중…</div>;
  if (status === "error")
    return (
      <div role="alert">
        불러오지 못했습니다. <button type="button">재시도</button>
      </div>
    );
  if (status === "empty" || !evidence) return <div role="status">이 인물의 근거 없음</div>;

  const options: SourceModeOption[] = [
    ...LAYERS.map((l) => ({
      value: l as SourceModeValue,
      disabled: !evidence.some((e) => e.source_layer === l),
      disabledReason: !evidence.some((e) => e.source_layer === l) ? "이 층위에서는 근거 없음" : undefined,
    })),
    { value: "비교" },
  ];

  const byLayer = (l: SourceLayer) => evidence.filter((e) => e.source_layer === l);

  return (
    <section aria-label={`${personName} 근거 비교`}>
      <h1>{personName}</h1>
      <SourceModeControl options={options} value={mode} onChange={setMode} />
      {evidence.some((e) => e.coding_validation_status !== "human_validated") && (
        <p className="coding-validation-notice" role="note">
          ⚠ 이 근거는 단일 AI 코딩 + 2차 AI 검증만 거쳤습니다 — 사람 검증 전입니다 (D-017)
        </p>
      )}
      <div className="evidence-comparison-grid">
        {(mode === "비교" ? LAYERS : [mode as SourceLayer]).map((layer) => {
          const rows = byLayer(layer);
          return (
            <div key={layer} className="evidence-layer-column">
              <h2>{LAYER_LABEL[layer]}</h2>
              {rows.length === 0 ? (
                <EvidenceCardEmpty layerLabel={LAYER_LABEL[layer]} />
              ) : (
                rows.map((e) => <EvidenceCard key={e.evidence_id} evidence={e} personName={personName} />)
              )}
            </div>
          );
        })}
      </div>
      <button type="button" onClick={() => onAskAI(personId)}>
        AI에게 물어보기
      </button>
    </section>
  );
}
