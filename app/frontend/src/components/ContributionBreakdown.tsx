import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { EvidenceSpan, SourceLayer } from "../api/types";

/**
 * design/component_spec.md `ContributionBreakdown` — "what-if weight-lab" (D-031, Q-012 option (a)).
 * Formula: analysis/scoring_model.md "What-if weight-lab formula". Client-side only, no backend
 * change (GET /v1/people/{id}/evidence already returns coding_label + source_layer for every row).
 * score_type is always "user_custom" here — this slice has no "default" composite score.
 * Labels are never summed into one number (heterogeneous, non-commensurable — see scoring_model.md).
 */

type WeightLayer = "HISTORY_BASE" | "HISTORY_ANNOTATION" | "ROMANCE";
const WEIGHT_LAYERS: WeightLayer[] = ["HISTORY_BASE", "HISTORY_ANNOTATION", "ROMANCE"];
const LAYER_LABEL: Record<WeightLayer, string> = {
  HISTORY_BASE: "정사 (역사책)",
  HISTORY_ANNOTATION: "정사 주석",
  ROMANCE: "연의 (소설)",
};

interface Props {
  personId?: string;
  personName?: string;
}

interface Contribution {
  label: string;
  weighted_emphasis: number;
  raw_total: number;
  per_layer_counts: Record<WeightLayer, number>;
  evidence_ids: string[];
}

type Weights = Record<WeightLayer, number>; // 0..100, independent (never forced to sum to 100)

/** Pure function so it can be unit-tested directly against the 曹操 worked example. */
export function computeContributions(evidence: EvidenceSpan[], weights: Weights): Contribution[] {
  const byLabel = new Map<string, Record<WeightLayer, { count: number; ids: string[] }>>();
  for (const row of evidence) {
    const layer = row.source_layer as WeightLayer;
    if (!WEIGHT_LAYERS.includes(layer)) continue; // LATER_INTERPRETATION/GAME_DATA never appear in this slice's evidence
    if (!byLabel.has(row.coding_label)) {
      byLabel.set(row.coding_label, {
        HISTORY_BASE: { count: 0, ids: [] },
        HISTORY_ANNOTATION: { count: 0, ids: [] },
        ROMANCE: { count: 0, ids: [] },
      });
    }
    const perLayer = byLabel.get(row.coding_label)!;
    perLayer[layer].count += 1;
    perLayer[layer].ids.push(row.evidence_id);
  }

  return Array.from(byLabel.entries()).map(([label, perLayer]) => {
    let weighted = 0;
    let raw = 0;
    const per_layer_counts = { HISTORY_BASE: 0, HISTORY_ANNOTATION: 0, ROMANCE: 0 };
    const evidence_ids: string[] = [];
    for (const layer of WEIGHT_LAYERS) {
      const count = perLayer[layer].count;
      per_layer_counts[layer] = count;
      raw += count;
      weighted += count * (weights[layer] / 100);
      evidence_ids.push(...perLayer[layer].ids);
    }
    return { label, weighted_emphasis: Math.round(weighted * 10) / 10, raw_total: raw, per_layer_counts, evidence_ids };
  });
}

export function totalByLayer(evidence: EvidenceSpan[]): Record<WeightLayer, number> {
  const totals: Record<WeightLayer, number> = { HISTORY_BASE: 0, HISTORY_ANNOTATION: 0, ROMANCE: 0 };
  for (const row of evidence) {
    const layer = row.source_layer as WeightLayer;
    if (layer in totals) totals[layer] += 1;
  }
  return totals;
}

export function ContributionBreakdown({ personId, personName }: Props) {
  const [evidence, setEvidence] = useState<EvidenceSpan[] | null>(null);
  const [status, setStatus] = useState<"loading" | "ok" | "error">("loading");
  const [weights, setWeights] = useState<Weights>({ HISTORY_BASE: 100, HISTORY_ANNOTATION: 100, ROMANCE: 100 });

  useEffect(() => {
    if (!personId) return;
    let cancelled = false;
    setStatus("loading");
    api
      .getEvidence(personId)
      .then((res) => {
        if (cancelled) return;
        setEvidence(res.evidence);
        setStatus("ok");
      })
      .catch(() => !cancelled && setStatus("error"));
    return () => {
      cancelled = true;
    };
  }, [personId]);

  if (!personId) {
    return (
      <section className="contribution-breakdown contribution-breakdown-no-person" role="status" aria-label="가중치 실험실">
        <p>인물을 먼저 선택하면, 정사와 연의 중 어디에 더 무게를 둘지 실험해볼 수 있어요.</p>
      </section>
    );
  }
  if (status === "loading") {
    return (
      <section className="contribution-breakdown" role="status" aria-label="가중치 실험실 로딩 중">
        불러오는 중…
      </section>
    );
  }
  if (status === "error" || !evidence) {
    return (
      <section className="contribution-breakdown" role="alert">
        불러오지 못했습니다. <button type="button">재시도</button>
      </section>
    );
  }

  const totals = totalByLayer(evidence);
  const zeroCoverageLayers = WEIGHT_LAYERS.filter((l) => totals[l] === 0);
  const activeLayers = WEIGHT_LAYERS.filter((l) => weights[l] > 0);
  const allWeightsZero = activeLayers.length === 0;
  const weightedZeroCoverageLayers = activeLayers.filter((l) => zeroCoverageLayers.includes(l));

  const contributions = computeContributions(evidence, weights)
    .filter((c) => c.weighted_emphasis > 0)
    .sort((a, b) => b.weighted_emphasis - a.weighted_emphasis);

  return (
    <section className="contribution-breakdown" role="region" aria-label={`${personName ?? personId} 가중치 실험실`}>
      <p className="score-type-badge user_custom">사용자 설정 점수 (진짜 능력치 아님)</p>
      <p className="weight-lab-intro">
        정사(정식 역사책)와 연의(재미있게 쓴 소설)는 같은 사람을 다르게 그릴 때가 있어요. 아래 막대를 움직여서
        "역사책 말만 믿어볼까?" 또는 "소설 말만 믿어볼까?"를 실험해보세요 — {personName ?? "이 인물"}에 대해 어떤
        이야기가 더 눈에 띄는지 달라지는 걸 볼 수 있어요.
      </p>

      <div className="weight-lab-sliders">
        {WEIGHT_LAYERS.map((layer) => (
          <div key={layer} className={`weight-lab-slider layer-${layer}`}>
            <label htmlFor={`weight-${layer}`}>{LAYER_LABEL[layer]}</label>
            <input
              id={`weight-${layer}`}
              type="range"
              min={0}
              max={100}
              value={weights[layer]}
              onChange={(e) => setWeights((w) => ({ ...w, [layer]: Number(e.target.value) }))}
              aria-valuetext={`${weights[layer]}%`}
            />
            <span className="weight-lab-value">{weights[layer]}%</span>
          </div>
        ))}
      </div>

      {allWeightsZero && (
        <p role="status" className="weight-lab-empty">
          모든 가중치가 0이에요. 막대를 움직여서 실험을 시작해보세요.
        </p>
      )}

      {!allWeightsZero && weightedZeroCoverageLayers.length > 0 && (
        <p role="status" className="weight-lab-zero-coverage-warning">
          ⚠ {weightedZeroCoverageLayers.map((l) => LAYER_LABEL[l]).join(", ")}에는 {personName ?? "이 인물"}의 근거가
          아예 없어요 — 가중치를 올려도 반영될 근거가 없습니다.
        </p>
      )}

      {!allWeightsZero && contributions.length > 0 && (
        <>
          <h3>이 가중치에서 부각되는 서술</h3>
          <ul className="weight-lab-contributions" data-testid="weight-lab-contributions">
            {contributions.map((c) => (
              <li key={c.label} className="weight-lab-contribution-row">
                <span className="weight-lab-label mono">{c.label}</span>
                <span className="weight-lab-emphasis" title="가중치 적용 값 (순위 아님)">
                  {c.weighted_emphasis}
                </span>
                <span className="weight-lab-per-layer">
                  {WEIGHT_LAYERS.map((l) => `${LAYER_LABEL[l]} ${c.per_layer_counts[l]}`).join(" · ")}
                </span>
                <span className="weight-lab-evidence-chips">
                  {c.evidence_ids.map((id) => (
                    <span key={id} className="evidence-chip">
                      {id}
                    </span>
                  ))}
                </span>
              </li>
            ))}
          </ul>
        </>
      )}

      {!allWeightsZero && contributions.length === 0 && weightedZeroCoverageLayers.length === 0 && (
        <p role="status">이 가중치 설정에서는 부각되는 서술이 없어요.</p>
      )}
    </section>
  );
}
