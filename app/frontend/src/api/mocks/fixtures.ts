/**
 * Mock fixtures for local dev + tests, shaped exactly like the Curated Export Transform's
 * output (app/architecture/system.md) would produce from the real research/evidence_matrix.csv
 * and analysis/outputs/result.json (as of the 30-row D-016 expansion pass). Content (excerpts,
 * labels, ids) is drawn from those real files, not invented — only the *shape* (structured
 * locator, array person_refs, float confidence, coding_validation_status) is synthesized here
 * to stand in for the not-yet-implemented transform (D-018).
 */
import type {
  EventResponse,
  EvidenceResponse,
  EvidenceSpan,
  Interpretation,
  MetricsResponse,
  PeopleResponse,
  RelationshipsResponse,
} from "../types";

const DATASET_VERSION = {
  pipeline_version: "1.0.0",
  run_id: "run-20260917T133031Z",
  generated_at: "2026-09-17T13:30:31Z",
  coding_validation_status: "human_validated" as const,
};

// confidence mapping mirrors the ADR-flagged high/medium string -> float rule (documented, not invented per-request)
const CONFIDENCE_MAP: Record<string, number> = { high: 0.85, medium: 0.6, low: 0.35 };

export const MOCK_PEOPLE: PeopleResponse = {
  event_id: "event.chibi",
  dataset_version: DATASET_VERSION,
  people: [
    {
      person_id: "person.cao_cao",
      canonical_name_zh: "曹操",
      canonical_name_ko: null,
      aliases: [{ alias: "孟德", type: "courtesy_name", observed_in: ["HISTORY_ANNOTATION"] }],
      evidence_coverage: { HISTORY_BASE: 2, HISTORY_ANNOTATION: 3, ROMANCE: 5 },
    },
    {
      person_id: "person.liu_bei",
      canonical_name_zh: "劉備",
      canonical_name_ko: null,
      aliases: [{ alias: "玄德", type: "courtesy_name", observed_in: ["ROMANCE"] }],
      evidence_coverage: { HISTORY_BASE: 1, HISTORY_ANNOTATION: 4, ROMANCE: 0 },
    },
    {
      person_id: "person.zhuge_liang",
      canonical_name_zh: "諸葛亮",
      canonical_name_ko: null,
      aliases: [{ alias: "孔明", type: "courtesy_name", observed_in: ["ROMANCE"] }],
      evidence_coverage: { HISTORY_BASE: 1, HISTORY_ANNOTATION: 1, ROMANCE: 7 },
    },
    {
      person_id: "person.sun_quan",
      canonical_name_zh: "孫權",
      canonical_name_ko: null,
      aliases: [{ alias: "仲謀", type: "courtesy_name", observed_in: ["HISTORY_ANNOTATION"] }],
      evidence_coverage: { HISTORY_BASE: 1, HISTORY_ANNOTATION: 5, ROMANCE: 0 },
    },
    {
      person_id: "person.zhou_yu",
      canonical_name_zh: "周瑜",
      canonical_name_ko: null,
      aliases: [{ alias: "公瑾", type: "courtesy_name", observed_in: ["HISTORY_ANNOTATION"] }],
      evidence_coverage: { HISTORY_BASE: 3, HISTORY_ANNOTATION: 5, ROMANCE: 4 },
    },
    {
      person_id: "person.huang_gai",
      canonical_name_zh: "黃蓋",
      canonical_name_ko: null,
      aliases: [],
      evidence_coverage: { HISTORY_BASE: 1, HISTORY_ANNOTATION: 1, ROMANCE: 2 },
    },
    {
      person_id: "person.guan_yu",
      canonical_name_zh: "關羽",
      canonical_name_ko: null,
      aliases: [{ alias: "雲長", type: "courtesy_name", observed_in: ["ROMANCE"] }],
      evidence_coverage: { HISTORY_BASE: 0, HISTORY_ANNOTATION: 1, ROMANCE: 4 },
    },
    {
      person_id: "person.lu_su",
      canonical_name_zh: "魯肅",
      canonical_name_ko: null,
      aliases: [],
      evidence_coverage: { HISTORY_BASE: 0, HISTORY_ANNOTATION: 4, ROMANCE: 1 },
    },
    {
      person_id: "person.zhao_yun",
      canonical_name_zh: "趙雲",
      canonical_name_ko: null,
      aliases: [{ alias: "子龍", type: "courtesy_name", observed_in: ["ROMANCE"] }],
      evidence_coverage: { HISTORY_BASE: 0, HISTORY_ANNOTATION: 0, ROMANCE: 3 },
    },
    {
      person_id: "person.guo_jia",
      canonical_name_zh: "郭嘉",
      canonical_name_ko: null,
      aliases: [{ alias: "奉孝", type: "courtesy_name", observed_in: ["ROMANCE"] }],
      evidence_coverage: { HISTORY_BASE: 0, HISTORY_ANNOTATION: 0, ROMANCE: 1 },
    },
  ],
};

export const MOCK_EVENT: EventResponse = {
  event_id: "event.chibi",
  event_name: "Battle of Red Cliffs",
  event_name_zh: "赤壁之戰",
  location: "長江赤壁",
  outcome: "Cao Cao's fleet defeated; retreat north",
  source_layer_coverage: ["HISTORY_BASE", "HISTORY_ANNOTATION", "ROMANCE"],
  participants: MOCK_PEOPLE.people.map((p) => ({
    person_id: p.person_id,
    role: "participant",
    source_layer: "HISTORY_BASE",
  })),
  dataset_version: DATASET_VERSION,
};

function evidence(row: Omit<EvidenceSpan, "coding_validation_status" | "confidence"> & { confidenceWord: "high" | "medium" }): EvidenceSpan {
  const { confidenceWord, ...rest } = row;
  return { ...rest, confidence: CONFIDENCE_MAP[confidenceWord], coding_validation_status: "human_validated" };
}

// Real rows from research/evidence_matrix.csv, reshaped to the curated-export EvidenceSpan contract.
// person.cao_cao's 10 rows match analysis/scoring_model.md's "What-if weight-lab formula" worked
// example exactly (2 HISTORY_BASE / 3 HISTORY_ANNOTATION / 5 ROMANCE) so weight-lab tests can assert
// against real, documented numbers rather than an invented fixture.
export const MOCK_EVIDENCE_BY_PERSON: Record<string, EvidenceSpan[]> = {
  "person.cao_cao": [
    evidence({
      evidence_id: "HB-J01-P1",
      source_layer: "HISTORY_BASE",
      work_title: "三國志",
      volume_or_chapter: "卷01 武帝紀",
      locator: { paragraph_index: 42 },
      permitted_excerpt: "公至赤壁，與備戰，不利。於是大疫，吏士多死者，乃引軍還。",
      coding_label: "military_setback_attribution",
      person_refs: ["person.cao_cao"],
      review_status: "single_coded",
      confidenceWord: "high",
      ambiguity_note: "Attributes retreat to disease, not enemy tactics.",
    }),
    evidence({
      evidence_id: "HB-J54-P2",
      source_layer: "HISTORY_BASE",
      work_title: "三國志",
      volume_or_chapter: "卷54 周瑜傳",
      locator: { paragraph_index: 18 },
      permitted_excerpt: "赤壁之役，值有疾病，孤燒船自退，橫使周瑜虛獲此名。",
      coding_label: "rival_credit_denial",
      person_refs: ["person.cao_cao", "person.zhou_yu"],
      review_status: "single_coded",
      confidenceWord: "high",
      ambiguity_note: null,
    }),
    evidence({
      evidence_id: "HA-J01-P1",
      source_layer: "HISTORY_ANNOTATION",
      work_title: "三國志裴松之注",
      volume_or_chapter: "卷01 武帝紀 annotation block",
      locator: { paragraph_index: 43 },
      permitted_excerpt: "劉備，吾儔也。但得計少晚；向使早放火，吾徒無類矣。",
      coding_label: "strategic_self_awareness",
      person_refs: ["person.cao_cao", "person.liu_bei"],
      review_status: "single_coded",
      confidenceWord: "medium",
      ambiguity_note: null,
    }),
    evidence({
      evidence_id: "HA-J01-P2",
      source_layer: "HISTORY_ANNOTATION",
      work_title: "三國志裴松之注",
      volume_or_chapter: "卷01 武帝紀 annotation block",
      locator: { paragraph_index: 44 },
      permitted_excerpt: "孫盛異同評曰：案吳志，劉備先破公軍，然後權攻合肥，而此記云權先攻合肥，後有赤壁之事。二者不同，吳志爲是。",
      coding_label: "source_conflict_note",
      person_refs: ["person.cao_cao", "person.liu_bei", "person.sun_quan"],
      review_status: "single_coded",
      confidenceWord: "high",
      ambiguity_note: null,
    }),
    evidence({
      evidence_id: "HA-J35-P2",
      source_layer: "HISTORY_ANNOTATION",
      work_title: "三國志裴松之注",
      volume_or_chapter: "卷35 諸葛亮傳 annotation block",
      locator: { paragraph_index: 12 },
      permitted_excerpt: "臣松之以為……關羽為曹公所獲，遇之甚厚，可謂能盡其用矣，猶義不背本，曾謂孔明之不若雲長乎！",
      coding_label: "peer_praise",
      person_refs: ["person.cao_cao", "person.guan_yu", "person.zhuge_liang"],
      review_status: "single_coded",
      confidenceWord: "medium",
      ambiguity_note: null,
    }),
    evidence({
      evidence_id: "RM-C049-P5",
      source_layer: "ROMANCE",
      work_title: "三國演義",
      volume_or_chapter: "第四十九回",
      locator: { paragraph_index: 30 },
      permitted_excerpt: "昔日曹操待足下甚厚，足下當有以報之。今日操兵敗，必走華容道。若令足下去時，必然放他過去。",
      coding_label: "strategic_manipulation_of_subordinate",
      person_refs: ["person.cao_cao", "person.zhuge_liang", "person.guan_yu"],
      review_status: "single_coded",
      confidenceWord: "medium",
      ambiguity_note: null,
    }),
    evidence({
      evidence_id: "RM-C050-P1",
      source_layer: "ROMANCE",
      work_title: "三國演義",
      volume_or_chapter: "第五十回",
      locator: { paragraph_index: 5 },
      permitted_excerpt: "曹操兵敗勢危，到此無路，望將軍以昔日之情為重。",
      coding_label: "appeal_to_past_favor",
      person_refs: ["person.cao_cao", "person.guan_yu"],
      review_status: "single_coded",
      confidenceWord: "high",
      ambiguity_note: null,
    }),
    evidence({
      evidence_id: "RM-C050-P2",
      source_layer: "ROMANCE",
      work_title: "三國演義",
      volume_or_chapter: "第五十回",
      locator: { paragraph_index: 8 },
      permitted_excerpt: "雲長是個義重如山之人……於是把馬頭勒回，謂眾軍曰：四散擺開。",
      coding_label: "loyalty_override_duty",
      person_refs: ["person.cao_cao", "person.guan_yu"],
      review_status: "single_coded",
      confidenceWord: "high",
      ambiguity_note: null,
    }),
    evidence({
      evidence_id: "RM-C050-P3",
      source_layer: "ROMANCE",
      work_title: "三國演義",
      volume_or_chapter: "第五十回",
      locator: { paragraph_index: 31 },
      permitted_excerpt: "吾哭郭奉孝耳！若奉孝在，決不使吾有此大失也！",
      coding_label: "leadership_self_reflection_regret",
      person_refs: ["person.cao_cao", "person.guo_jia"],
      review_status: "single_coded",
      confidenceWord: "high",
      ambiguity_note: "Contrasts sharply with HB-J54-P2's denial of fault — the slice's key divergence example.",
    }),
    evidence({
      evidence_id: "RM-C050-P4",
      source_layer: "ROMANCE",
      work_title: "三國演義",
      volume_or_chapter: "第五十回",
      locator: { paragraph_index: 34 },
      permitted_excerpt: "亮夜觀乾象，操賊未合身亡。留這人情，教雲長做了，亦是美事。",
      coding_label: "fatalistic_strategic_foresight",
      person_refs: ["person.cao_cao", "person.zhuge_liang", "person.guan_yu"],
      review_status: "single_coded",
      confidenceWord: "high",
      ambiguity_note: null,
    }),
  ],
  "person.zhao_yun": [
    evidence({
      evidence_id: "RM-C049-P4",
      source_layer: "ROMANCE",
      work_title: "三國演義",
      volume_or_chapter: "第四十九回",
      locator: { paragraph_index: 25 },
      permitted_excerpt: "吾已料定都督不能容我，必來加害，預先教趙子龍來相接。",
      coding_label: "foresight_escape_planning",
      person_refs: ["person.zhao_yun", "person.zhuge_liang"],
      review_status: "single_coded",
      confidenceWord: "high",
      ambiguity_note: null,
    }),
    evidence({
      evidence_id: "RM-C049-P7",
      source_layer: "ROMANCE",
      work_title: "三國演義",
      volume_or_chapter: "第四十九回",
      locator: { paragraph_index: 40 },
      permitted_excerpt: "趙雲拈弓搭箭，立於船尾大叫曰：吾乃常山趙子龍也！……箭到處，射斷徐盛船上篷索。",
      coding_label: "combat_skill_display",
      person_refs: ["person.zhao_yun"],
      review_status: "single_coded",
      confidenceWord: "high",
      ambiguity_note: null,
    }),
    evidence({
      evidence_id: "RM-C052-P1",
      source_layer: "ROMANCE",
      work_title: "三國演義",
      volume_or_chapter: "第五十二回",
      locator: { paragraph_index: 10 },
      permitted_excerpt: "趙雲挺槍出馬……兩馬相交，戰到四五合，陳應料敵不過……雲將陳應活捉過馬。",
      coding_label: "combat_skill_display",
      person_refs: ["person.zhao_yun"],
      review_status: "single_coded",
      confidenceWord: "medium",
      ambiguity_note: null,
    }),
  ],
  "person.zhou_yu": [
    evidence({
      evidence_id: "HB-J54-P1",
      source_layer: "HISTORY_BASE",
      work_title: "三國志",
      volume_or_chapter: "卷54 周瑜傳",
      locator: { paragraph_index: 12 },
      permitted_excerpt: "瑜部將黃蓋曰：今寇眾我寡，難與持久……可燒而走也。",
      coding_label: "subordinate_initiated_strategy",
      person_refs: ["person.zhou_yu", "person.huang_gai"],
      review_status: "single_coded",
      confidenceWord: "high",
      ambiguity_note: "Huang Gai originates; Zhou Yu authorizes.",
    }),
    evidence({
      evidence_id: "RM-C049-P3",
      source_layer: "ROMANCE",
      work_title: "三國演義",
      volume_or_chapter: "第四十九回",
      locator: { paragraph_index: 22 },
      permitted_excerpt: "此人有奪天地造化之法，鬼神不測之術！……及早殺卻，免生他日之憂。",
      coding_label: "rival_elimination_attempt",
      person_refs: ["person.zhou_yu", "person.zhuge_liang"],
      review_status: "single_coded",
      confidenceWord: "high",
      ambiguity_note: null,
    }),
  ],
  "person.liu_bei": [
    evidence({
      evidence_id: "HB-J32-P1",
      source_layer: "HISTORY_BASE",
      work_title: "三國志",
      volume_or_chapter: "卷32 先主傳",
      locator: { paragraph_index: 9 },
      permitted_excerpt: "與曹公戰於赤壁，大破之，焚其舟船。先主與吳軍水陸並進，追到南郡。",
      coding_label: "joint_military_command",
      person_refs: ["person.liu_bei"],
      review_status: "single_coded",
      confidenceWord: "high",
      ambiguity_note: null,
    }),
  ],
};

export const MOCK_METRICS: MetricsResponse = {
  event_id: "event.chibi",
  dataset_version: DATASET_VERSION,
  population: {
    n: 30,
    description:
      "30 coded evidence spans covering 10 named persons in the 적벽대전 vertical slice, across HISTORY_BASE, HISTORY_ANNOTATION, and ROMANCE. Cast size is derived at run time, not fixed.",
  },
  metrics: [
    {
      metric_id: "coverage.PERSON-CAOCAO.HISTORY_BASE",
      name: "Evidence-span coverage count: 曹操 (HISTORY_BASE)",
      value: 2,
      unit: "evidence_span_count",
      interval_low: null,
      interval_high: null,
      method: "Count of evidence_matrix.csv rows for this person/layer.",
    },
    {
      metric_id: "divergence.caocao_selfreflection",
      name: "Divergence: Cao Cao's self-reflection after the Red Cliffs defeat",
      value: null,
      unit: "categorical_classification",
      interval_low: null,
      interval_high: null,
      method:
        "classification=contradictory; evidence_ids=HB-J54-P2,RM-C050-P3; rationale: HISTORY_BASE denies fault; ROMANCE admits fault and blames Guo Jia's death.",
    },
  ],
  limitations: [
    "N=30 evidence spans — far too small for any inferential statistic.",
    "This entire evidence set was coded by AI agents only (LLM-LLM double-coding check on the original 22 rows, κ=0.90); no human review yet (D-017).",
  ],
  warnings: [
    "Do not compute or display a composite/weighted score — none exists in this slice.",
    "coverage.* = 0 means 'no coded span', never a score of zero.",
  ],
};

export const MOCK_RELATIONSHIPS: RelationshipsResponse = {
  event_id: "event.chibi",
  dataset_version: DATASET_VERSION,
  no_centrality_computed: true,
  edges: [
    {
      edge_id: "edge.hb.huanggai.zhouyu.1",
      from_person_id: "person.huang_gai",
      to_person_id: "person.zhou_yu",
      relation_type: "advises",
      direction: "directed",
      source_layer: "HISTORY_BASE",
      confidence: 0.85,
      evidence_refs: ["HB-J54-P1"],
    },
    {
      edge_id: "edge.rm.zhouyu.zhugeliang.1",
      from_person_id: "person.zhou_yu",
      to_person_id: "person.zhuge_liang",
      relation_type: "opposes",
      direction: "directed",
      source_layer: "ROMANCE",
      confidence: 0.85,
      evidence_refs: ["RM-C049-P3"],
    },
  ],
};

export function mockEvidenceResponse(personId: string): EvidenceResponse {
  return {
    person_id: personId,
    dataset_version: DATASET_VERSION,
    evidence: MOCK_EVIDENCE_BY_PERSON[personId] ?? [],
  };
}

export const MOCK_INTERPRETATION_GROUNDED: Interpretation = {
  interpretation_id: "interp-chibi-caocao-selfreflection-001",
  answer_mode: "비교",
  status: "ok",
  generated_at: "2026-09-17T13:00:00Z",
  model: { name: "claude-sonnet-5", version: "2026-09" },
  prompt_version: "llm_contract_v1_answer_mode_비교",
  input_refs: {
    result_json_run_id: "run-20260917T122003Z",
    evidence_matrix_checksum: "288a68e027fcd6799d1b15efd5b6f6b27fdc619e83105ca2a00d6c9be5370865",
  },
  coding_validation_notice:
    "이 근거 코딩은 AI 단독 검증(2차 AI 코더와의 일치도 Cohen's kappa=0.90)이며, 아직 사람 검증 전 단계입니다.",
  claims: [
    {
      claim_id: "c1",
      claim_type: "observation",
      text: "정사에서 曹操는 적벽 패전의 책임을 전염병 탓으로 돌립니다.",
      evidence_refs: ["HB-J54-P2"],
      metric_refs: [],
      confidence: "high",
    },
    {
      claim_id: "c3",
      claim_type: "interpretation",
      text: "두 서술은 정반대의 자기 평가를 보여주는 사례로 'contradictory'로 분류됩니다.",
      evidence_refs: ["HB-J54-P2", "RM-C050-P3"],
      metric_refs: ["divergence.caocao_selfreflection"],
      confidence: "medium",
      caveats: ["이 근거는 단일 AI 코더가 최초 코딩했고 2차 AI 코더 검증만 거쳤습니다 — 사람 검증 전입니다."],
    },
  ],
};

export const MOCK_INTERPRETATION_ABSTAIN: Interpretation = {
  interpretation_id: "interp-chibi-caocao-gamedata-refuse-001",
  answer_mode: "게임",
  status: "insufficient_evidence",
  generated_at: "2026-09-17T13:05:00Z",
  model: { name: "claude-sonnet-5", version: "2026-09" },
  prompt_version: "llm_contract_v1_answer_mode_게임",
  input_refs: {
    result_json_run_id: "run-20260917T122003Z",
    evidence_matrix_checksum: "288a68e027fcd6799d1b15efd5b6f6b27fdc619e83105ca2a00d6c9be5370865",
  },
  abstention_reason: "이 슬라이스에는 승인된 GAME_DATA 소스가 없습니다.",
  claims: [],
};
