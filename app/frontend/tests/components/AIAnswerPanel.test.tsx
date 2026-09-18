import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { axe } from "../setup/axe";
import { AIAnswerPanel } from "../../src/components/AIAnswerPanel";
import { MOCK_INTERPRETATION_GROUNDED, MOCK_INTERPRETATION_ABSTAIN } from "../../src/api/mocks/fixtures";

describe("AIAnswerPanel", () => {
  it("renders evidence-id chips for a grounded claim", () => {
    render(<AIAnswerPanel answerMode="비교" onAsk={() => {}} result={MOCK_INTERPRETATION_GROUNDED} />);
    expect(screen.getAllByText("HB-J54-P2").length).toBeGreaterThan(0);
    expect(screen.getByText("RM-C050-P3")).toBeInTheDocument();
  });

  it("always shows the D-017 disclosure when evidence is cited", () => {
    render(<AIAnswerPanel answerMode="비교" onAsk={() => {}} result={MOCK_INTERPRETATION_GROUNDED} />);
    expect(screen.getByText(/AI 단독 검증/)).toBeInTheDocument();
  });

  it("renders an explicit abstention state distinct from an answered claim, with the reason", () => {
    render(<AIAnswerPanel answerMode="게임" onAsk={() => {}} result={MOCK_INTERPRETATION_ABSTAIN} />);
    expect(screen.getByText(/답변을 보류합니다/)).toBeInTheDocument();
    expect(screen.getByText(/승인된 GAME_DATA 소스가 없습니다/)).toBeInTheDocument();
  });

  it("renders a retryable error state distinct from abstention", () => {
    render(<AIAnswerPanel answerMode="비교" onAsk={() => {}} result={null} error />);
    expect(screen.getByRole("alert")).toHaveTextContent("연결할 수 없습니다");
  });

  it("has no axe accessibility violations", async () => {
    const { container } = render(
      <AIAnswerPanel answerMode="비교" onAsk={() => {}} result={MOCK_INTERPRETATION_GROUNDED} />
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
