import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import BookingSuccess from "./BookingSuccess";

import { booking } from "../test/testData";

describe("BookingSuccess", () => {
  it("renders ticket details", () => {
    render(
      <BookingSuccess
        booking={booking}
        onBookAnother={vi.fn()}
        onManageBooking={vi.fn()}
      />,
    );

    expect(screen.getByText("Your train ticket is ready")).toBeInTheDocument();

    expect(screen.getByText("TRN-ABC12345")).toBeInTheDocument();

    expect(screen.getByText("Test Passenger")).toBeInTheDocument();

    expect(screen.getByText("Colombo Fort")).toBeInTheDocument();

    expect(screen.getByText("Kandy")).toBeInTheDocument();
  });

  it("starts another booking", async () => {
    const user = userEvent.setup();
    const onBookAnother = vi.fn();

    render(
      <BookingSuccess
        booking={booking}
        onBookAnother={onBookAnother}
        onManageBooking={vi.fn()}
      />,
    );

    await user.click(
      screen.getByRole("button", {
        name: /book another journey/i,
      }),
    );

    expect(onBookAnother).toHaveBeenCalledOnce();
  });

  it("opens manage booking with reference", async () => {
    const user = userEvent.setup();
    const onManageBooking = vi.fn();

    render(
      <BookingSuccess
        booking={booking}
        onBookAnother={vi.fn()}
        onManageBooking={onManageBooking}
      />,
    );

    await user.click(
      screen.getByRole("button", {
        name: /manage this booking/i,
      }),
    );

    expect(onManageBooking).toHaveBeenCalledWith("TRN-ABC12345");
  });
});
