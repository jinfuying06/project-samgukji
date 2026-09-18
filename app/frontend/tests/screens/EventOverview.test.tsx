import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { EventOverview } from "../../src/screens/EventOverview";
import { MOCK_PEOPLE } from "../../src/api/mocks/fixtures";

describe("EventOverview (integration, mocked API)", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({ ok: true, json: async () => MOCK_PEOPLE }))
    );
  });
  afterEach(() => vi.unstubAllGlobals());

  it("shows a loading state, then the full 10-person cast without hardcoding a count (D-016)", async () => {
    render(<EventOverview eventId="event.chibi" onSelectPerson={() => {}} onStartQuest={() => {}} />);
    expect(screen.getByRole("status")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("曹操")).toBeInTheDocument());
    expect(screen.getAllByRole("button").filter((b) => b.textContent && /^[一-鿿]+$/.test(b.textContent))).toHaveLength(
      MOCK_PEOPLE.people.length
    );
  });

  it("renders an explicit error state on fetch failure, not a blank screen", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({ ok: false, status: 500, json: async () => ({ error_code: "x", message: "x" }) }))
    );
    render(<EventOverview eventId="event.chibi" onSelectPerson={() => {}} onStartQuest={() => {}} />);
    await waitFor(() => expect(screen.getByRole("alert")).toBeInTheDocument());
  });
});
