import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { axe } from "../setup/axe";
import { ScoreCard } from "../../src/components/ScoreCard";
import type { Metric } from "../../src/api/types";

const coverageZero: Metric = {
  metric_id: "coverage.PERSON-LIUBEI.ROMANCE",
  name: "Evidence-span coverage count: 劉備 (ROMANCE)",
  value: 0,
  unit: "evidence_span_count",
};

const divergenceMetric: Metric = {
  metric_id: "divergence.caocao_selfreflection",
  name: "Divergence: Cao Cao self-reflection",
  value: null,
  unit: "categorical_classification",
  method: "classification=contradictory; evidence_ids=HB-J54-P2,RM-C050-P3; rationale: x",
};

describe("ScoreCard", () => {
  it("renders the insufficient_data state instead of a fabricated composite score", () => {
    render(<ScoreCard metric={null} scoreType="insufficient_data" />);
    expect(screen.getByText(/아직 합성 점수 없음/)).toBeInTheDocument();
  });

  it("never renders a 0 coverage count the same way as an insufficient_data state (distinct DOM)", () => {
    const { container } = render(<ScoreCard metric={coverageZero} scoreType="default" />);
    expect(screen.getByText("0")).toBeInTheDocument();
    expect(container.querySelector(".score-card-insufficient")).toBeNull();
  });

  it("renders a divergence classification as a labeled badge, not a number", () => {
    render(<ScoreCard metric={divergenceMetric} scoreType="default" />);
    expect(screen.getByText("contradictory")).toBeInTheDocument();
  });

  it("has no axe accessibility violations", async () => {
    const { container } = render(<ScoreCard metric={coverageZero} scoreType="default" />);
    expect(await axe(container)).toHaveNoViolations();
  });
});
