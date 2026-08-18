import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import BookingDetails from "./BookingDetails";

import { booking, cancelledBooking } from "../test/testData";

describe("BookingDetails", () => {
  it("shows confirmed booking", () => {
    render(
      <BookingDetails
        booking={booking}
        cancelling={false}
        onCancel={vi.fn()}
      />,
    );

    expect(screen.getByText("TRN-ABC12345")).toBeInTheDocument();

    expect(screen.getByText("CONFIRMED")).toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: /cancel booking/i,
      }),
    ).toBeInTheDocument();
  });

  it("calls cancel handler", async () => {
    const user = userEvent.setup();
    const onCancel = vi.fn();

    render(
      <BookingDetails
        booking={booking}
        cancelling={false}
        onCancel={onCancel}
      />,
    );

    await user.click(
      screen.getByRole("button", {
        name: /cancel booking/i,
      }),
    );

    expect(onCancel).toHaveBeenCalledOnce();
  });

  it("does not show cancel button for cancelled booking", () => {
    render(
      <BookingDetails
        booking={cancelledBooking}
        cancelling={false}
        onCancel={vi.fn()}
      />,
    );

    expect(screen.getByText("CANCELLED")).toBeInTheDocument();

    expect(
      screen.queryByRole("button", {
        name: /^cancel booking$/i,
      }),
    ).not.toBeInTheDocument();
  });
});
