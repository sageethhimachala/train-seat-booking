import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import SeatCard from "./SeatCard";

const seat = {
  seat_id: 1,
  coach_number: 1,
  seat_number: "01",
};

describe("SeatCard", () => {
  it("displays seat information", () => {
    render(<SeatCard seat={seat} selected={false} onSelect={vi.fn()} />);

    expect(screen.getByText("01")).toBeInTheDocument();

    expect(screen.getByText("Coach 1")).toBeInTheDocument();
  });

  it("calls onSelect with seat when clicked", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();

    render(<SeatCard seat={seat} selected={false} onSelect={onSelect} />);

    await user.click(
      screen.getByRole("button", {
        name: /coach 1, seat 01/i,
      }),
    );

    expect(onSelect).toHaveBeenCalledWith(seat);
  });

  it("indicates selected state", () => {
    render(<SeatCard seat={seat} selected onSelect={vi.fn()} />);

    expect(screen.getByRole("button")).toHaveAttribute("aria-pressed", "true");
  });
});
