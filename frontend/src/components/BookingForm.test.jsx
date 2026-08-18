import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import BookingForm from "./BookingForm";

import { availability } from "../test/testData";

const selectedSeat = availability.available_seats[0];

describe("BookingForm", () => {
  it("does not render without selected seat", () => {
    const { container } = render(
      <BookingForm
        selectedSeat={null}
        availability={availability}
        loading={false}
        onSubmit={vi.fn()}
      />,
    );

    expect(container).toBeEmptyDOMElement();
  });

  it("renders passenger form when seat is selected", () => {
    render(
      <BookingForm
        selectedSeat={selectedSeat}
        availability={availability}
        loading={false}
        onSubmit={vi.fn()}
      />,
    );

    expect(screen.getByLabelText("Passenger name")).toBeInTheDocument();

    expect(screen.getByLabelText("Email address")).toBeInTheDocument();
  });

  it("submits correct booking payload", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(
      <BookingForm
        selectedSeat={selectedSeat}
        availability={availability}
        loading={false}
        onSubmit={onSubmit}
      />,
    );

    await user.type(screen.getByLabelText("Passenger name"), "Sageeth");

    await user.type(
      screen.getByLabelText("Email address"),
      "sageeth@example.com",
    );

    await user.click(
      screen.getByRole("button", {
        name: /confirm booking/i,
      }),
    );

    expect(onSubmit).toHaveBeenCalledWith({
      trip_id: 10,
      seat_id: 1,
      origin_station_id: 1,
      destination_station_id: 3,
      passenger_name: "Sageeth",
      passenger_email: "sageeth@example.com",
    });
  });

  it("disables submit with invalid form", () => {
    render(
      <BookingForm
        selectedSeat={selectedSeat}
        availability={availability}
        loading={false}
        onSubmit={vi.fn()}
      />,
    );

    expect(
      screen.getByRole("button", {
        name: /confirm booking/i,
      }),
    ).toBeDisabled();
  });
});
