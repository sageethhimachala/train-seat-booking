import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import BookingLookupForm from "./BookingLookupForm";

describe("BookingLookupForm", () => {
  it("normalizes booking reference to uppercase", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<BookingLookupForm loading={false} onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText("Booking reference"), "trn-abc12345");

    await user.click(
      screen.getByRole("button", {
        name: /find booking/i,
      }),
    );

    expect(onSubmit).toHaveBeenCalledWith("TRN-ABC12345");
  });

  it("disables button when reference is empty", () => {
    render(<BookingLookupForm loading={false} onSubmit={vi.fn()} />);

    expect(
      screen.getByRole("button", {
        name: /find booking/i,
      }),
    ).toBeDisabled();
  });
});
