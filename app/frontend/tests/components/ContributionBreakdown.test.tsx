import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { axe } from "../setup/axe";
import { ContributionBreakdown, computeContributions, totalByLayer } from "../../src/components/ContributionBreakdown";
import { MOCK_EVIDENCE_BY_PERSON, mockEvidenceResponse } from "../../src/api/mocks/fixtures";

const CAOCAO_EVIDENCE = MOCK_EVIDENCE_BY_PERSON["person.cao_cao"];

describe("computeContributions (pure formula, analysis/scoring_model.md worked example)", () => {
  it("정사 100% only surfaces the 2 HISTORY_BASE labels, nothing else", () => {
    const result = computeContributions(CAOCAO_EVIDENCE, { HISTORY_BASE: 100, HISTORY_ANNOTATION: 0, ROMANCE: 0 });
    const nonzero = result.filter((c) => c.weighted_emphasis > 0).map((c) => c.label);
    expect(nonzero.sort()).toEqual(["military_setback_attribution", "rival_credit_denial"].sort());
  });

  it("정사주석 100% only surfaces the 3 HISTORY_ANNOTATION labels", () => {
    const result = computeContributions(CAOCAO_EVIDENCE, { HISTORY_BASE: 0, HISTORY_ANNOTATION: 100, ROMANCE: 0 });
    const nonzero = result.filter((c) => c.weighted_emphasis > 0).map((c) => c.label);
    expect(nonzero.sort()).toEqual(["peer_praise", "source_conflict_note", "strategic_self_awareness"].sort());
  });

  it("연의 100% only surfaces the 5 ROMANCE labels", () => {
    const result = computeContributions(CAOCAO_EVIDENCE, { HISTORY_BASE: 0, HISTORY_ANNOTATION: 0, ROMANCE: 100 });
    const nonzero = result.filter((c) => c.weighted_emphasis > 0).map((c) => c.label);
    expect(nonzero.sort()).toEqual(
      [
        "appeal_to_past_favor",
        "fatalistic_strategic_foresight",
        "leadership_self_reflection_regret",
        "loyalty_override_duty",
        "strategic_manipulation_of_subordinate",
      ].sort()
    );
  });

  it("weighted_emphasis scales linearly with the layer weight (50% halves a single-layer label)", () => {
    const full = computeContributions(CAOCAO_EVIDENCE, { HISTORY_BASE: 100, HISTORY_ANNOTATION: 0, ROMANCE: 0 });
    const half = computeContributions(CAOCAO_EVIDENCE, { HISTORY_BASE: 50, HISTORY_ANNOTATION: 0, ROMANCE: 0 });
    const fullRow = full.find((c) => c.label === "military_setback_attribution")!;
    const halfRow = half.find((c) => c.label === "military_setback_attribution")!;
    expect(halfRow.weighted_emphasis).toBeCloseTo(fullRow.weighted_emphasis / 2, 5);
  });

  it("never sums two different labels into one number (each label stays its own row)", () => {
    const result = computeContributions(CAOCAO_EVIDENCE, { HISTORY_BASE: 100, HISTORY_ANNOTATION: 100, ROMANCE: 100 });
    const labels = new Set(result.map((c) => c.label));
    expect(labels.size).toBe(result.length); // one row per label, no merging
  });
});

describe("totalByLayer", () => {
  it("computes 曹操's real per-layer totals (2 HB / 3 HA / 5 RM)", () => {
    expect(totalByLayer(CAOCAO_EVIDENCE)).toEqual({ HISTORY_BASE: 2, HISTORY_ANNOTATION: 3, ROMANCE: 5 });
  });

  it("computes 趙雲's real per-layer totals (0 HB / 0 HA / 3 RM) — the zero-coverage test case", () => {
    expect(totalByLayer(MOCK_EVIDENCE_BY_PERSON["person.zhao_yun"])).toEqual({
      HISTORY_BASE: 0,
      HISTORY_ANNOTATION: 0,
      ROMANCE: 3,
    });
  });
});

describe("ContributionBreakdown (integration)", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url: string) => {
        const personId = url.split("/people/")[1]?.split("/")[0];
        return { ok: true, json: async () => mockEvidenceResponse(personId) };
      })
    );
  });
  afterEach(() => vi.unstubAllGlobals());

  it("renders a prompt, not the weight lab, when no person is selected", () => {
    render(<ContributionBreakdown personId={undefined} />);
    expect(screen.getByText(/인물을 먼저 선택하면/)).toBeInTheDocument();
    expect(screen.queryByRole("slider")).not.toBeInTheDocument();
  });

  it("labels the result as user_custom, never default, and shows the plain-language intro", async () => {
    render(<ContributionBreakdown personId="person.cao_cao" personName="曹操" />);
    await waitFor(() => expect(screen.getByText(/사용자 설정 점수/)).toBeInTheDocument());
    expect(screen.getByText(/정사\(정식 역사책\)와 연의\(재미있게 쓴 소설\)/)).toBeInTheDocument();
  });

  it("shows the zero_coverage_warning when a weight is raised on a layer with 0 evidence for this person (趙雲, HISTORY_BASE)", async () => {
    render(<ContributionBreakdown personId="person.zhao_yun" personName="趙雲" />);
    await waitFor(() => expect(screen.getByLabelText("정사 (역사책)")).toBeInTheDocument());
    // default weights start at 100/100/100, so the warning should already be visible for 趙雲's zero-coverage layers
    const warning = screen.getByText(/근거가\s*아예 없어요/);
    expect(warning).toBeInTheDocument();
    expect(warning.textContent).toContain("정사 (역사책)");
    expect(warning.textContent).toContain("정사 주석");
  });

  it("recomputes the breakdown immediately when a slider changes, no network re-fetch needed", async () => {
    render(<ContributionBreakdown personId="person.cao_cao" personName="曹操" />);
    await waitFor(() => expect(screen.getByLabelText("연의 (소설)")).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText("정사 (역사책)"), { target: { value: "0" } });
    fireEvent.change(screen.getByLabelText("정사 주석"), { target: { value: "0" } });
    // now only ROMANCE weighted -> military_setback_attribution (HISTORY_BASE-only label) must disappear
    await waitFor(() => expect(screen.queryByText("military_setback_attribution")).not.toBeInTheDocument());
    expect(screen.getByText("leadership_self_reflection_regret")).toBeInTheDocument();
  });

  it("never renders ranking/capability language", async () => {
    render(<ContributionBreakdown personId="person.cao_cao" personName="曹操" />);
    await waitFor(() => expect(screen.getByText(/이 가중치에서 부각되는 서술/)).toBeInTheDocument());
    expect(screen.queryByText(/능력치 순위/)).not.toBeInTheDocument();
    expect(screen.queryByText(/최강/)).not.toBeInTheDocument();
  });

  it("has no axe accessibility violations", async () => {
    const { container } = render(<ContributionBreakdown personId="person.cao_cao" personName="曹操" />);
    await waitFor(() => expect(screen.getByText(/사용자 설정 점수/)).toBeInTheDocument());
    expect(await axe(container)).toHaveNoViolations();
  });
});
