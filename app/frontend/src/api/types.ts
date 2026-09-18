/**
 * TypeScript types mirroring app/architecture/api_contract.yaml's components.schemas.
 * Do not add a field here that the contract/schemas don't define (agents/frontend.md 금지:
 * "계약에 없는 필드를 임의 추정하지 않습니다").
 */

export type SourceLayer =
  | "HISTORY_BASE"
  | "HISTORY_ANNOTATION"
  | "ROMANCE"
  | "LATER_INTERPRETATION"
  | "GAME_DATA";

export type AnswerMode = "정사" | "연의" | "비교" | "게임";

export type CodingValidationStatus = "llm_llm_validated_only" | "human_validated";

export interface ErrorResponse {
  error_code: string;
  message: string;
}

export interface DatasetVersionRef {
  pipeline_version: string;
  run_id: string;
  generated_at?: string;
  coding_validation_status: CodingValidationStatus;
}

export interface Population {
  n: number;
  description: string;
}

export interface Metric {
  metric_id: string;
  name: string;
  value: number | null;
  unit: string;
  interval_low?: number | null;
  interval_high?: number | null;
  method?: string;
}

export interface PersonAlias {
  alias: string;
  type: string;
  observed_in: SourceLayer[];
}

export interface Person {
  person_id: string;
  canonical_name_zh: string;
  canonical_name_ko?: string | null;
  aliases: PersonAlias[];
}

export interface PersonWithCoverage extends Person {
  evidence_coverage: Partial<Record<SourceLayer, number>>;
}

export interface EventParticipant {
  person_id: string;
  role: string;
  source_layer: SourceLayer;
  evidence_refs?: string[];
}

export interface EventEntity {
  event_id: string;
  event_name: string;
  event_name_zh?: string;
  location?: string | null;
  participants: EventParticipant[];
  outcome?: string | null;
  source_layer_coverage: SourceLayer[];
}

export interface EvidenceLocator {
  paragraph_index: number;
  annotation_index?: number | null;
  char_start?: number | null;
  char_end?: number | null;
}

/** Curated-export shape (data/schemas/evidence.schema.json) — NOT the raw research/evidence_matrix.csv shape. */
export interface EvidenceSpan {
  evidence_id: string;
  source_layer: SourceLayer;
  work_title: string;
  edition_ref?: string | null;
  volume_or_chapter: string;
  locator: EvidenceLocator;
  permitted_excerpt?: string | null;
  coding_label: string;
  person_refs?: string[];
  confidence: number; // 0-1 float, normalized by the Curated Export Transform (D-018)
  review_status: "unreviewed" | "single_coded" | "double_coded" | "adjudicated";
  coding_validation_status: CodingValidationStatus; // row-level mirror of D-017 disclosure
  ambiguity_note?: string | null;
}

export interface RelationshipEdge {
  edge_id: string;
  from_person_id: string;
  to_person_id: string;
  relation_type: string;
  direction: "directed" | "undirected";
  source_layer: SourceLayer;
  confidence: number;
  evidence_refs: string[];
}

export interface EventResponse extends EventEntity {
  dataset_version: DatasetVersionRef;
}

export interface PeopleResponse {
  event_id: string;
  dataset_version: DatasetVersionRef;
  people: PersonWithCoverage[];
}

export interface EvidenceResponse {
  person_id: string;
  dataset_version: DatasetVersionRef;
  evidence: EvidenceSpan[];
}

export type MetricKind = "coverage" | "label_frequency" | "divergence";

export interface MetricsResponse {
  event_id: string;
  dataset_version: DatasetVersionRef;
  population: Population;
  metrics: Metric[];
  limitations: string[];
  warnings?: string[];
}

export interface RelationshipsResponse {
  event_id: string;
  dataset_version: DatasetVersionRef;
  edges: RelationshipEdge[];
  no_centrality_computed: true;
}

export type ClaimType = "observation" | "interpretation" | "recommendation";
export type ClaimConfidence = "high" | "medium" | "low";

export interface InterpretationClaim {
  claim_id: string;
  claim_type: ClaimType;
  text: string;
  evidence_refs: string[];
  metric_refs: string[];
  confidence: ClaimConfidence;
  caveats?: string[];
}

export interface Interpretation {
  interpretation_id: string;
  answer_mode: AnswerMode;
  status: "ok" | "insufficient_evidence" | "abstained";
  generated_at: string;
  model: { name: string; version: string };
  prompt_version: string;
  input_refs: { result_json_run_id: string; evidence_matrix_checksum: string };
  abstention_reason?: string;
  coding_validation_notice?: string;
  claims: InterpretationClaim[];
}

export interface AskRequest {
  event_id: string;
  question: string;
  answer_mode: AnswerMode;
}

/** score_type per product/data_to_ui_mapping.md — insufficient_data is this slice's default (no composite score exists). */
export type ScoreType = "default" | "user_custom" | "external_game" | "insufficient_data";
