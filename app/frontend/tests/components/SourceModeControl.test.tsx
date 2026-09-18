import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { axe } from "../setup/axe";
import { SourceModeControl, type SourceModeOption } from "../../src/components/SourceModeControl";

const options: SourceModeOption[] = [
  { value: "HISTORY_BASE" },
  { value: "HISTORY_ANNOTATION", disabled: true, disabledReason: "이 층위에서는 근거 없음" },
  { value: "ROMANCE" },
];

describe("SourceModeControl", () => {
  it("renders required text labels, never enum strings, and marks the selected option", () => {
    render(<SourceModeControl options={options} value="HISTORY_BASE" onChange={() => {}} />);
    expect(screen.getByRole("radio", { name: "정사" })).toHaveAttribute("aria-checked", "true");
    expect(screen.queryByText("HISTORY_BASE")).not.toBeInTheDocument();
  });

  it("exposes the disabled reason via aria-describedby, not color alone", () => {
    render(<SourceModeControl options={options} value="HISTORY_BASE" onChange={() => {}} />);
    const disabledOption = screen.getByRole("radio", { name: "정사 주석" });
    const describedBy = disabledOption.getAttribute("aria-describedby");
    expect(describedBy).toBeTruthy();
    expect(screen.getByText("이 층위에서는 근거 없음")).toHaveAttribute("id", describedBy!);
  });

  it("does not call onChange when a disabled option is clicked", async () => {
    const onChange = vi.fn();
    render(<SourceModeControl options={options} value="HISTORY_BASE" onChange={onChange} />);
    await userEvent.click(screen.getByRole("radio", { name: "정사 주석" }));
    expect(onChange).not.toHaveBeenCalled();
  });

  it("has no axe accessibility violations", async () => {
    const { container } = render(<SourceModeControl options={options} value="HISTORY_BASE" onChange={() => {}} />);
    expect(await axe(container)).toHaveNoViolations();
  });
});
