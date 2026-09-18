import { describe, it, expect, beforeAll } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import yaml from "js-yaml";
import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import {
  MOCK_EVENT,
  MOCK_PEOPLE,
  MOCK_METRICS,
  MOCK_RELATIONSHIPS,
  MOCK_EVIDENCE_BY_PERSON,
  MOCK_INTERPRETATION_GROUNDED,
  MOCK_INTERPRETATION_ABSTAIN,
} from "../../src/api/mocks/fixtures";

/**
 * Drift check: validates this frontend's mock fixtures against the FROZEN
 * app/architecture/api_contract.yaml (agents/frontend.md 완료 조건: "API mock과 실제
 * 계약 간 drift 검사"). Also cross-checks Interpretation fixtures against the standalone
 * analysis/schemas/interpretation.schema.json, since api_contract.yaml states that schema
 * is "Duplicated here only for OpenAPI tooling; the JSON Schema file is the source of truth".
 */

const REPO_ROOT = resolve(__dirname, "../../../..");

function rewriteRefs(node: unknown): unknown {
  if (Array.isArray(node)) return node.map(rewriteRefs);
  if (node && typeof node === "object") {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(node as Record<string, unknown>)) {
      if (k === "$ref" && typeof v === "string") {
        out[k] = v.replace("#/components/schemas/", "#/$defs/");
      } else {
        out[k] = rewriteRefs(v);
      }
    }
    return out;
  }
  return node;
}

let ajv: Ajv2020;
let defs: Record<string, unknown>;

beforeAll(() => {
  const yamlText = readFileSync(resolve(REPO_ROOT, "app/architecture/api_contract.yaml"), "utf-8");
  const spec = yaml.load(yamlText) as { components: { schemas: Record<string, unknown> } };
  defs = rewriteRefs(spec.components.schemas) as Record<string, unknown>;
  ajv = new Ajv2020({ strict: false, allErrors: true });
  addFormats(ajv);
});

function validateAgainst(schemaName: string, value: unknown) {
  const schema = { $defs: defs, $ref: `#/$defs/${schemaName}` };
  const validate = ajv.compile(schema);
  const valid = validate(value);
  return { valid, errors: validate.errors };
}

describe("mock fixtures vs. frozen api_contract.yaml (drift check)", () => {
  it("MOCK_EVENT matches the Event+dataset_version response shape", () => {
    const { valid, errors } = validateAgainst("Event", MOCK_EVENT);
    expect(errors, JSON.stringify(errors)).toBeNull();
    expect(valid).toBe(true);
  });

  it("every person in MOCK_PEOPLE matches Person+evidence_coverage", () => {
    for (const person of MOCK_PEOPLE.people) {
      const { valid, errors } = validateAgainst("Person", person);
      expect(errors, `${person.person_id}: ${JSON.stringify(errors)}`).toBeNull();
      expect(valid).toBe(true);
    }
  });

  it("every EvidenceSpan fixture matches the curated-export EvidenceSpan schema", () => {
    for (const rows of Object.values(MOCK_EVIDENCE_BY_PERSON)) {
      for (const row of rows) {
        const { valid, errors } = validateAgainst("EvidenceSpan", row);
        expect(errors, `${row.evidence_id}: ${JSON.stringify(errors)}`).toBeNull();
        expect(valid).toBe(true);
      }
    }
  });

  it("every Metric in MOCK_METRICS matches the Metric schema", () => {
    for (const metric of MOCK_METRICS.metrics) {
      const { valid, errors } = validateAgainst("Metric", metric);
      expect(errors, `${metric.metric_id}: ${JSON.stringify(errors)}`).toBeNull();
      expect(valid).toBe(true);
    }
  });

  it("every RelationshipEdge in MOCK_RELATIONSHIPS matches its schema", () => {
    for (const edge of MOCK_RELATIONSHIPS.edges) {
      const { valid, errors } = validateAgainst("RelationshipEdge", edge);
      expect(errors, `${edge.edge_id}: ${JSON.stringify(errors)}`).toBeNull();
      expect(valid).toBe(true);
    }
  });

  it("Interpretation fixtures match api_contract.yaml's inline Interpretation schema", () => {
    for (const interp of [MOCK_INTERPRETATION_GROUNDED, MOCK_INTERPRETATION_ABSTAIN]) {
      const { valid, errors } = validateAgainst("Interpretation", interp);
      expect(errors, `${interp.interpretation_id}: ${JSON.stringify(errors)}`).toBeNull();
      expect(valid).toBe(true);
    }
  });
});

describe("Interpretation fixtures vs. the authoritative analysis/schemas/interpretation.schema.json", () => {
  it("both worked examples validate against the standalone JSON Schema file (source of truth per api_contract.yaml)", () => {
    const schema = JSON.parse(
      readFileSync(resolve(REPO_ROOT, "analysis/schemas/interpretation.schema.json"), "utf-8")
    );
    const localAjv = new Ajv2020({ strict: false, allErrors: true });
    addFormats(localAjv);
    const validate = localAjv.compile(schema);
    for (const interp of [MOCK_INTERPRETATION_GROUNDED, MOCK_INTERPRETATION_ABSTAIN]) {
      const valid = validate(interp);
      expect(validate.errors, `${interp.interpretation_id}: ${JSON.stringify(validate.errors)}`).toBeNull();
      expect(valid).toBe(true);
    }
  });
});
