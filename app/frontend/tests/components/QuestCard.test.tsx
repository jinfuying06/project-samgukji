import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "../setup/axe";
import { QuestCard, type QuestState } from "../../src/components/QuestCard";

const baseState: QuestState = {
  requiresLayers: ["HISTORY_BASE", "ROMANCE"],
  requiresCounterEvidence: true,
  evidenceSeenIds: [],
  counterEvidenceIds: ["RM-C050-P3"],
  evidenceLayerById: { "HB-J54-P2": "HISTORY_BASE", "RM-C050-P3": "ROMANCE" },
};

describe("QuestCard", () => {
  it("keeps the complete button aria-disabled until both layers are seen (AC-5)", () => {
    render(<QuestCard goal="test" state={baseState} onOpenEvidence={() => {}} />);
    expect(screen.getByRole("button", { name: "완료" })).toHaveAttribute("aria-disabled", "true");
  });

  it("stays aria-disabled with one layer seen but no counter-evidence acknowledged", () => {
    const state = { ...baseState, evidenceSeenIds: ["HB-J54-P2"] };
    render(<QuestCard goal="test" state={state} onOpenEvidence={() => {}} />);
    expect(screen.getByRole("button", { name: "완료" })).toHaveAttribute("aria-disabled", "true");
    expect(screen.getByText(/아직 확인하지 않은 출처/)).toBeInTheDocument();
  });

  it("becomes enabled only once both layers and counter-evidence are satisfied", () => {
    const state = { ...baseState, evidenceSeenIds: ["HB-J54-P2", "RM-C050-P3"] };
    render(<QuestCard goal="test" state={state} onOpenEvidence={() => {}} />);
    expect(screen.getByRole("button", { name: "완료" })).toHaveAttribute("aria-disabled", "false");
  });

  it("the complete button is never removed from the DOM, even when unmet", () => {
    render(<QuestCard goal="test" state={baseState} onOpenEvidence={() => {}} />);
    expect(screen.getByRole("button", { name: "완료" })).toBeInTheDocument();
  });

  it("calls onOpenEvidence when an evidence item is clicked", async () => {
    const onOpen = vi.fn();
    render(<QuestCard goal="test" state={baseState} onOpenEvidence={onOpen} />);
    await userEvent.click(screen.getByRole("button", { name: /RM-C050-P3/ }));
    expect(onOpen).toHaveBeenCalledWith("RM-C050-P3");
  });

  it("has no axe accessibility violations", async () => {
    const { container } = render(<QuestCard goal="test" state={baseState} onOpenEvidence={() => {}} />);
    expect(await axe(container)).toHaveNoViolations();
  });
});
