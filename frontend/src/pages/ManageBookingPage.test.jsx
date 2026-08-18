import { render, screen, waitFor } from "@testing-library/react";

import userEvent from "@testing-library/user-event";

import { beforeEach, describe, expect, it, vi } from "vitest";

import ManageBookingPage from "./ManageBookingPage";

import { booking, cancelledBooking } from "../test/testData";

import { cancelBooking, getBooking } from "../services/bookingService";

vi.mock("../services/bookingService", () => ({
  getBooking: vi.fn(),
  cancelBooking: vi.fn(),
}));

describe("ManageBookingPage", () => {
  beforeEach(() => {
    getBooking.mockResolvedValue(booking);

    cancelBooking.mockResolvedValue(cancelledBooking);
  });

  it("finds booking by reference", async () => {
    const user = userEvent.setup();

    render(<ManageBookingPage />);

    await user.type(screen.getByLabelText("Booking reference"), "TRN-ABC12345");

    await user.click(
      screen.getByRole("button", {
        name: /find booking/i,
      }),
    );

    await waitFor(() => {
      expect(getBooking).toHaveBeenCalledWith("TRN-ABC12345");
    });

    expect(await screen.findByText("Test Passenger")).toBeInTheDocument();
  });

  it("cancels booking after confirmation", async () => {
    const user = userEvent.setup();

    render(<ManageBookingPage initialBookingReference="TRN-ABC12345" />);

    expect(await screen.findByText("Test Passenger")).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", {
        name: /^cancel booking$/i,
      }),
    );

    expect(screen.getByRole("dialog")).toBeInTheDocument();

    await user.click(
      screen.getByRole("button", {
        name: /yes, cancel booking/i,
      }),
    );

    await waitFor(() => {
      expect(cancelBooking).toHaveBeenCalledWith("TRN-ABC12345");
    });

    expect(await screen.findByText("CANCELLED")).toBeInTheDocument();
  });
});
