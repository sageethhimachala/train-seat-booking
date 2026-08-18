import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import SeatSelection from "./SeatSelection";

import { availability } from "../test/testData";

describe("SeatSelection", () => {
  it("renders available seats", () => {
    render(
      <SeatSelection
        availability={availability}
        selectedSeat={null}
        onSelectSeat={vi.fn()}
      />,
    );

    expect(screen.getByText("Select a reserved seat")).toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: /coach 1, seat 01/i,
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: /coach 1, seat 04/i,
      }),
    ).toBeInTheDocument();
  });

  it("selects a seat", async () => {
    const user = userEvent.setup();
    const onSelectSeat = vi.fn();

    render(
      <SeatSelection
        availability={availability}
        selectedSeat={null}
        onSelectSeat={onSelectSeat}
      />,
    );

    await user.click(
      screen.getByRole("button", {
        name: /coach 1, seat 02/i,
      }),
    );

    expect(onSelectSeat).toHaveBeenCalledWith(availability.available_seats[1]);
  });

  it("shows no-seat state when no trip exists", () => {
    render(
      <SeatSelection
        availability={{
          ...availability,
          trip: null,
          available_seats: [],
          message: "No trains with available seats.",
        }}
        selectedSeat={null}
        onSelectSeat={vi.fn()}
      />,
    );

    expect(screen.getByText("No seats available")).toBeInTheDocument();

    expect(
      screen.getByText("No trains with available seats."),
    ).toBeInTheDocument();
  });
});
