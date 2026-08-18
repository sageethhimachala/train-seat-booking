import { render, screen, waitFor } from "@testing-library/react";

import userEvent from "@testing-library/user-event";

import { beforeEach, describe, expect, it, vi } from "vitest";

import BookingPage from "./BookingPage";

import { availability, booking, stations } from "../test/testData";

import { getStations } from "../services/stationService";

import { searchAvailability } from "../services/availabilityService";

import { createBooking } from "../services/bookingService";

vi.mock("../services/stationService", () => ({
  getStations: vi.fn(),
}));

vi.mock("../services/availabilityService", () => ({
  searchAvailability: vi.fn(),
}));

vi.mock("../services/bookingService", () => ({
  createBooking: vi.fn(),
}));

describe("BookingPage", () => {
  beforeEach(() => {
    getStations.mockResolvedValue(stations);

    searchAvailability.mockResolvedValue(availability);

    createBooking.mockResolvedValue(booking);
  });

  it("loads stations on startup", async () => {
    render(<BookingPage onManageBooking={vi.fn()} />);

    await waitFor(() => {
      expect(getStations).toHaveBeenCalledOnce();
    });

    expect(await screen.findByText("Plan your journey")).toBeInTheDocument();
  });

  it("completes booking flow", async () => {
    const user = userEvent.setup();

    render(<BookingPage onManageBooking={vi.fn()} />);

    const origin = await screen.findByLabelText("Origin station");

    const destination = screen.getByLabelText("Destination station");

    await user.selectOptions(origin, "1");

    await user.selectOptions(destination, "3");

    await user.click(
      screen.getByRole("button", {
        name: /search available seats/i,
      }),
    );

    await waitFor(() => {
      expect(searchAvailability).toHaveBeenCalledWith(1, 3);
    });

    const seatButton = await screen.findByRole("button", {
      name: /coach 1, seat 01/i,
    });

    await user.click(seatButton);

    await user.type(screen.getByLabelText("Passenger name"), "Test Passenger");

    await user.type(screen.getByLabelText("Email address"), "test@example.com");

    await user.click(
      screen.getByRole("button", {
        name: /confirm booking/i,
      }),
    );

    await waitFor(() => {
      expect(createBooking).toHaveBeenCalledWith({
        trip_id: 10,
        seat_id: 1,
        origin_station_id: 1,
        destination_station_id: 3,
        passenger_name: "Test Passenger",
        passenger_email: "test@example.com",
      });
    });

    expect(
      await screen.findByText("Your train ticket is ready"),
    ).toBeInTheDocument();

    expect(screen.getByText("TRN-ABC12345")).toBeInTheDocument();
  });
});
