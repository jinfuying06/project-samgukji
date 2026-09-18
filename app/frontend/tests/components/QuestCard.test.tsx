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
    render(<QuestCard goal="test" state={baseState} onOpenEvidence={() => {}} onComplete={() => {}} />);
    expect(screen.getByRole("button", { name: "완료" })).toHaveAttribute("aria-disabled", "true");
  });

  it("stays aria-disabled with one layer seen but no counter-evidence acknowledged", () => {
    const state = { ...baseState, evidenceSeenIds: ["HB-J54-P2"] };
    render(<QuestCard goal="test" state={state} onOpenEvidence={() => {}} onComplete={() => {}} />);
    expect(screen.getByRole("button", { name: "완료" })).toHaveAttribute("aria-disabled", "true");
    expect(screen.getByText(/아직 확인하지 않은 출처/)).toBeInTheDocument();
  });

  it("becomes enabled only once both layers and counter-evidence are satisfied", () => {
    const state = { ...baseState, evidenceSeenIds: ["HB-J54-P2", "RM-C050-P3"] };
    render(<QuestCard goal="test" state={state} onOpenEvidence={() => {}} onComplete={() => {}} />);
    expect(screen.getByRole("button", { name: "완료" })).toHaveAttribute("aria-disabled", "false");
  });

  it("the complete button is never removed from the DOM, even when unmet", () => {
    render(<QuestCard goal="test" state={baseState} onOpenEvidence={() => {}} onComplete={() => {}} />);
    expect(screen.getByRole("button", { name: "완료" })).toBeInTheDocument();
  });

  it("calls onOpenEvidence when an evidence item is clicked", async () => {
    const onOpen = vi.fn();
    render(<QuestCard goal="test" state={baseState} onOpenEvidence={onOpen} onComplete={() => {}} />);
    await userEvent.click(screen.getByRole("button", { name: /RM-C050-P3/ }));
    expect(onOpen).toHaveBeenCalledWith("RM-C050-P3");
  });

  it("renders a clickable button for every required-layer evidence item, not just counter-evidence (real-UI reachability bug found by live testing)", async () => {
    // Regression: previously only counterEvidenceIds were rendered, so a real user
    // could never open HB-J54-P2 and the layersSatisfied gate could never become true
    // through the actual UI -- only by injecting evidenceSeenIds directly, as the other
    // tests in this file do.
    const onOpen = vi.fn();
    render(<QuestCard goal="test" state={baseState} onOpenEvidence={onOpen} onComplete={() => {}} />);
    const historyButton = screen.getByRole("button", { name: /HB-J54-P2/ });
    expect(historyButton).toBeInTheDocument();
    await userEvent.click(historyButton);
    expect(onOpen).toHaveBeenCalledWith("HB-J54-P2");
  });

  it("does NOT call onComplete when '완료' is clicked while the gate is unmet", async () => {
    const onComplete = vi.fn();
    render(<QuestCard goal="test" state={baseState} onOpenEvidence={() => {}} onComplete={onComplete} />);
    await userEvent.click(screen.getByRole("button", { name: "완료" }));
    expect(onComplete).not.toHaveBeenCalled();
  });

  it("calls onComplete when '완료' is clicked once the gate is satisfied (real-browser testing found this button previously did nothing when clicked)", async () => {
    const state = { ...baseState, evidenceSeenIds: ["HB-J54-P2", "RM-C050-P3"] };
    const onComplete = vi.fn();
    render(<QuestCard goal="test" state={state} onOpenEvidence={() => {}} onComplete={onComplete} />);
    await userEvent.click(screen.getByRole("button", { name: "완료" }));
    expect(onComplete).toHaveBeenCalledTimes(1);
  });

  it("has no axe accessibility violations", async () => {
    const { container } = render(<QuestCard goal="test" state={baseState} onOpenEvidence={() => {}} onComplete={() => {}} />);
    expect(await axe(container)).toHaveNoViolations();
  });
});
