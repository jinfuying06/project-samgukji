import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { axe } from "../setup/axe";
import { EvidenceCard, EvidenceCardEmpty } from "../../src/components/EvidenceCard";
import { MOCK_EVIDENCE_BY_PERSON } from "../../src/api/mocks/fixtures";

const sample = MOCK_EVIDENCE_BY_PERSON["person.cao_cao"][0];

describe("EvidenceCard", () => {
  it("renders the llm_llm_validated_only disclosure when that is the real status", () => {
    render(<EvidenceCard evidence={{ ...sample, coding_validation_status: "llm_llm_validated_only" }} personName="曹操" />);
    expect(screen.getByText(/AI 단독 검증만 완료/)).toBeInTheDocument();
  });

  it("renders human_validated status distinctly, matching the current dataset (D-024)", () => {
    render(<EvidenceCard evidence={sample} personName="曹操" />);
    expect(screen.getByText("사람 검증 완료")).toBeInTheDocument();
    expect(screen.queryByText(/AI 단독 검증만 완료/)).not.toBeInTheDocument();
  });

  it("always renders the D-017 coding-validation disclosure, never suppressed", () => {
    render(<EvidenceCard evidence={sample} personName="曹操" />);
    expect(
      screen.getByText(/사람 검증 완료|AI 단독 검증만 완료/)
    ).toBeInTheDocument();
  });

  it("renders a distinct empty state for a missing layer, not blank space", () => {
    render(<EvidenceCardEmpty layerLabel="연의" />);
    expect(screen.getByRole("status")).toHaveTextContent("이 층위(연의)에서는 근거 없음");
  });

  it("has no axe accessibility violations", async () => {
    const { container } = render(<EvidenceCard evidence={sample} personName="曹操" />);
    expect(await axe(container)).toHaveNoViolations();
  });
});
