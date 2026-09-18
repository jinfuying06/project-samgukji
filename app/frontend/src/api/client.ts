import type {
  AskRequest,
  ErrorResponse,
  EventResponse,
  EvidenceResponse,
  Interpretation,
  MetricKind,
  MetricsResponse,
  PeopleResponse,
  RelationshipsResponse,
  SourceLayer,
} from "./types";

/**
 * Thin typed fetch wrapper for app/architecture/api_contract.yaml's /v1/* endpoints.
 * Never recomputes or reinterprets a server value (agents/frontend.md 필수 규칙).
 */

export class ApiError extends Error {
  status: number;
  code: string;
  constructor(status: number, body: ErrorResponse) {
    super(body.message);
    this.status = status;
    this.code = body.error_code;
  }
}

const BASE = "/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = (await res.json().catch(() => ({
      error_code: "unknown_error",
      message: `HTTP ${res.status}`,
    }))) as ErrorResponse;
    throw new ApiError(res.status, body);
  }
  return (await res.json()) as T;
}

export const api = {
  getEvent: (eventId: string) => request<EventResponse>(`/events/${eventId}`),

  getPeople: (eventId: string) => request<PeopleResponse>(`/events/${eventId}/people`),

  getEvidence: (personId: string, opts?: { eventId?: string; sourceLayer?: SourceLayer }) => {
    const params = new URLSearchParams();
    if (opts?.eventId) params.set("event_id", opts.eventId);
    if (opts?.sourceLayer) params.set("source_layer", opts.sourceLayer);
    const qs = params.toString();
    return request<EvidenceResponse>(`/people/${personId}/evidence${qs ? `?${qs}` : ""}`);
  },

  getMetrics: (eventId: string, kind?: MetricKind) => {
    const qs = kind ? `?kind=${kind}` : "";
    return request<MetricsResponse>(`/events/${eventId}/metrics${qs}`);
  },

  getRelationships: (eventId: string, sourceLayer?: SourceLayer) => {
    const qs = sourceLayer ? `?source_layer=${sourceLayer}` : "";
    return request<RelationshipsResponse>(`/events/${eventId}/relationships${qs}`);
  },

  ask: (body: AskRequest) =>
    request<Interpretation>(`/ask`, { method: "POST", body: JSON.stringify(body) }),
};
