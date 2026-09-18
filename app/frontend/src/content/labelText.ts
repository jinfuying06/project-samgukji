/**
 * Korean, elementary-school-friendly display text for raw technical strings that the data
 * model exposes (`coding_label`, divergence `classification`, `metric_id`/`metric.value`).
 *
 * This file changes DISPLAY TEXT ONLY. It never changes underlying data values — components
 * still store/compare the raw English strings (`coding_label`, `classification`, `metric_id`);
 * this module only maps them to short Korean names + one-sentence explanations for rendering.
 *
 * Translations are based on the real label definitions in `research/coding_manual.md`
 * (label set table) and the real divergence case list in
 * `analysis/pipelines/compute_chibi_result.py` (`divergence_cases`). Where a definition's
 * nuance is hard to compress into one child-friendly sentence without losing meaning, a
 * comment says so explicitly rather than silently oversimplifying.
 */

export interface KoLabelEntry {
  name: string;
  explain: string;
}

/**
 * All 24 `coding_label` values used in this slice (research/coding_manual.md "Label set"
 * table). Keys are exactly the raw `coding_label` strings from the data — never invent a new
 * key here that isn't in the manual.
 */
export const CODING_LABEL_KO: Record<string, KoLabelEntry> = {
  military_setback_attribution: {
    name: "전쟁에서 진 이유 설명",
    explain: "싸움에서 지거나 물러난 일에 대해, 왜 그랬는지 이유(예: 병이 돌았다)를 분명히 밝혀주는 기록이에요.",
  },
  // Nuance that's hard to compress faithfully: this label is explicitly ROMANCE-only, and the
  // manual is careful to say the illness is a *narrative device*, not a real medical/personality
  // diagnosis (coding_manual.md's non-negotiable rules). The explanation below keeps "진짜 병이
  // 아니라" wording on purpose so a child doesn't read it as "이 사람은 정신병이 있었다".
  psychosomatic_strategic_anxiety: {
    name: "고민 때문에 아팠다는 이야기 (연의에만)",
    explain: "《연의》(소설)에만 나오는 이야기로, 실제 병 때문이 아니라 풀리지 않은 전략 고민 때문에 몸이 아팠다고 그려요.",
  },
  joint_military_command: {
    name: "여러 사람이 함께 지휘",
    explain: "두 명 이상의 사람이 함께 그 군사 작전의 성과를 인정받는 기록이에요.",
  },
  minimal_narrative_role: {
    name: "이름만 나오고 활약은 없음",
    explain: "그 사람이 그 사건이 벌어질 때 있었다고는 나오지만, 직접 무언가를 하거나 말했다고는 나오지 않아요.",
  },
  decisive_leadership_under_dissent: {
    name: "반대를 무릅쓴 결정",
    explain: "많은 부하들이 반대했는데도 지도자가 자기 뜻대로 결정을 내리는 모습을 보여줘요.",
  },
  subordinate_initiated_strategy: {
    name: "부하가 낸 아이디어",
    explain: "부하가 먼저 전략을 제안하고, 윗사람이 그것을 허락하거나 실행에 옮기는 기록이에요.",
  },
  rival_credit_denial: {
    name: "경쟁자의 공을 깎아내림",
    explain: "누군가의 말이 경쟁자가 세운 공을 인정하지 않거나 자기 것으로 돌리는 내용이에요.",
  },
  strategic_self_awareness: {
    name: "스스로 실수를 인정함",
    explain: "다른 사람 탓을 하지 않고, 자기가 위험했거나 실수했다는 걸 스스로 깨닫고 말하는 기록이에요.",
  },
  source_conflict_note: {
    name: "기록끼리 다르다는 지적",
    explain: "주석(설명 글)이 같은 사건을 다룬 두 기록이 서로 다르다고 분명히 짚어주는 내용이에요.",
  },
  // Subtle but real distinction from source_conflict_note: this one is about *why* a record
  // might be untrustworthy (편 들기), not about two records simply disagreeing. Kept separate
  // on purpose so the child-friendly text doesn't blur the two together.
  source_bias_flag: {
    name: "한쪽 편이라는 지적",
    explain: "주석이 어떤 기록은 한쪽(예: 오나라 쪽)에 유리하게 쓰였을 수 있다고 짚어주는 내용이에요.",
  },
  deceptive_communication: {
    name: "적을 속이는 메시지",
    explain: "상대를 속이려고 일부러 꾸며서 보낸 메시지를, 실제로 있었던 전략으로 다루는 기록이에요.",
  },
  peer_praise: {
    name: "동료를 칭찬함",
    explain: "한 사람이 다른 사람의 구체적인 능력이나 행동을 들어 칭찬하는 말이에요.",
  },
  leadership_attribution_acknowledgment: {
    name: "성공을 남의 덕으로 인정함",
    explain: "지도자가 자기 성공이 다른 특정한 사람 덕분이라고 직접 말하는 기록이에요.",
  },
  supernatural_attribution: {
    name: "신비한 능력 이야기 (연의에만)",
    explain: "《연의》(소설)에만 나오는 이야기로, 어떤 사람이 의식이나 예언으로 날씨나 운명을 바꿀 수 있다고 그려요.",
  },
  rival_elimination_attempt: {
    name: "경쟁자를 없애려는 계획",
    explain: "정면 전투가 아닌 방법으로 경쟁자나 동료를 없애거나 제거하려는 계획을 보여주는 기록이에요.",
  },
  foresight_escape_planning: {
    name: "미리 준비해둔 도망 계획",
    explain: "어떤 일이 실제로 벌어지기 전에, 미리 도망갈 방법을 준비해둔 기록이에요.",
  },
  strategic_manipulation_of_subordinate: {
    name: "부하를 시험하는 계획",
    explain: "누군가 부하의 마음(충성심이나 의무감)을 시험하려고 일부러 임무나 상황을 만든 기록이에요.",
  },
  appeal_to_past_favor: {
    name: "예전 은혜를 상기시킴",
    explain: "누군가 예전에 받은 도움이나 은혜를 이야기하면서 지금의 결정을 바꾸려고 하는 기록이에요.",
  },
  loyalty_override_duty: {
    name: "의리가 명령보다 앞섬",
    explain: "누군가 정식 명령이나 약속보다 개인적인 의리를 더 중요하게 여기고 선택하는 모습이에요.",
  },
  leadership_self_reflection_regret: {
    name: "지난 선택을 후회함",
    explain: "지도자가 과거의 결정이 잘못이었다고 스스로 후회하며 인정하는 기록이에요.",
  },
  fatalistic_strategic_foresight: {
    name: "운명을 미리 안다는 이야기 (연의에만)",
    explain: "《연의》(소설)에만 나오는 이야기로, 누군가 점이나 하늘의 뜻으로 앞일(예: 누가 언제 죽을지)을 미리 안다고 말해요.",
  },
  alliance_persuasion: {
    name: "동맹을 맺자고 설득함",
    explain: "한 사람이 다른 지도자나 세력에게, 다른 선택 대신 자기편과 동맹을 맺자고 설득하는 기록이에요.",
  },
  // ROMANCE-only "by convention in this slice" per the manual (no comparable HISTORY_BASE/
  // HISTORY_ANNOTATION combat set-pieces were found), not ROMANCE-exclusive "by construction"
  // like supernatural_attribution/fatalistic_strategic_foresight. The short Korean name below
  // keeps that softer framing ("주로") rather than stating an absolute rule.
  combat_skill_display: {
    name: "무예 실력을 직접 보여줌 (주로 연의)",
    explain: "전략을 짜는 게 아니라, 활쏘기나 일대일 대결처럼 그 사람의 무예 실력을 직접 보여주는 장면이에요.",
  },
  reciprocal_combat_mercy: {
    name: "싸우다가 봐준 일",
    explain: "일대일로 싸우다가 그 순간 생긴 존중 때문에 상대를 살려주는 모습이에요 (예전 은혜나 명령 때문이 아니에요).",
  },
};

/**
 * Divergence-case `classification` values (analysis/pipelines/compute_chibi_result.py
 * `divergence_cases`). Keys are exactly the raw `classification` strings from `metric.method`.
 */
export const DIVERGENCE_CLASSIFICATION_KO: Record<
  "contradictory" | "complementary" | "compatible",
  KoLabelEntry
> = {
  contradictory: {
    name: "서로 반대로 말해요",
    explain: "정사와 연의가 같은 일을 놓고 서로 다르게, 반대로 이야기하고 있어요.",
  },
  complementary: {
    name: "서로 다른 부분을 말해요",
    explain: "반대는 아니고, 각자 다른 면을 보여줘요.",
  },
  compatible: {
    name: "똑같이 말해요",
    explain: "두 이야기가 서로 일치해요.",
  },
};

/** `source_layer` -> long, parenthetical Korean form used inside metric sentences. */
export const SOURCE_LAYER_KO_LONG: Record<string, string> = {
  HISTORY_BASE: "정사(역사책)",
  HISTORY_ANNOTATION: "정사 주석(역사책에 달린 설명)",
  ROMANCE: "연의(소설)",
  LATER_INTERPRETATION: "후대 연구·해석",
  GAME_DATA: "게임 자료",
};

/**
 * Display-name lookup for the `PERSON-*` tokens used inside `coverage.<PERSON_ID>.<LAYER>`
 * metric ids (mirrors analysis/pipelines/compute_chibi_result.py's own DISPLAY_NAME map for
 * this slice's 10-person cast — kept here only for UI display text, not as a new data source).
 */
const PERSON_ID_KO: Record<string, string> = {
  "PERSON-CAOCAO": "曹操",
  "PERSON-LIUBEI": "劉備",
  "PERSON-ZHUGELIANG": "諸葛亮",
  "PERSON-SUNQUAN": "孫權",
  "PERSON-ZHOUYU": "周瑜",
  "PERSON-HUANGGAI": "黃蓋",
  "PERSON-GUANYU": "關羽",
  "PERSON-LUSU": "魯肅",
  "PERSON-ZHAOYUN": "趙雲",
  "PERSON-GUOJIA": "郭嘉",
};

/**
 * Short Korean paraphrase of each divergence case's `name` field (compute_chibi_result.py
 * `divergence_cases`), keyed by the `case_id` suffix after `divergence.`. Used only for the
 * plain-sentence display of a divergence metric's *topic* — the case's `classification`
 * (contradictory/complementary/compatible) is rendered separately via
 * `DIVERGENCE_CLASSIFICATION_KO`.
 */
const DIVERGENCE_CASE_KO: Record<string, string> = {
  caocao_selfreflection: "曹操가 적벽에서 진 뒤 자기 잘못을 인정했는지",
  liubei_role_reliability: "劉備가 큰 역할을 했다는 이야기를 얼마나 믿을 수 있는지",
  fireattack_originator: "불로 공격하자는 생각을 누가 먼저 냈는지",
  lusu_origination_credit: "曹操에 맞서자는 계획을 누가 먼저 냈는지",
  huanggai_feigned_surrender: "黃蓋의 거짓 투항 속임수",
  huanggai_wound: "黃蓋가 화살에 맞은 상황",
  zhouyu_lusu_succession: "周瑜가 죽으면서 魯肅을 후계자로 추천한 일",
};

/**
 * Turns a raw `metric_id` (+ its `value`) into one plain Korean sentence for display.
 * Supported metric_id shapes (analysis/pipelines/compute_chibi_result.py):
 *   - `coverage.<PERSON_ID>.<LAYER>`      e.g. coverage.PERSON-CAOCAO.HISTORY_BASE
 *   - `label_frequency.<coding_label>`    e.g. label_frequency.military_setback_attribution
 *   - `divergence.<case_id>`              e.g. divergence.caocao_selfreflection
 * Never changes the underlying metric_id/value — this only produces display text.
 */
export function metricToKoreanSentence(metricId: string, value: number | null): string {
  const dotIndex = metricId.indexOf(".");
  if (dotIndex === -1) return metricId;
  const kind = metricId.slice(0, dotIndex);
  const rest = metricId.slice(dotIndex + 1);

  if (kind === "coverage") {
    const [personId, layer] = rest.split(".");
    const personKo = PERSON_ID_KO[personId] ?? personId;
    const layerKo = SOURCE_LAYER_KO_LONG[layer] ?? layer;
    const countText = value === null ? "알 수 없음" : `${value}건`;
    return `${personKo} - ${layerKo}에 나온 근거: ${countText}`;
  }

  if (kind === "label_frequency") {
    const entry = CODING_LABEL_KO[rest];
    const name = entry ? entry.name : rest;
    const countText = value === null ? "알 수 없음" : `${value}건`;
    return `"${name}" 이야기가 나온 횟수: ${countText}`;
  }

  if (kind === "divergence") {
    const title = DIVERGENCE_CASE_KO[rest] ?? "정사와 연의 이야기 차이";
    return `이야기 차이 사례: ${title}`;
  }

  return metricId;
}
