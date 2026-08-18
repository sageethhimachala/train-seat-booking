import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import ConfirmationModal from "./ConfirmationModal";

describe("ConfirmationModal", () => {
  it("does not render when closed", () => {
    render(
      <ConfirmationModal
        open={false}
        title="Cancel this booking?"
        message="Are you sure?"
        onConfirm={vi.fn()}
        onCancel={vi.fn()}
      />,
    );

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("renders when open", () => {
    render(
      <ConfirmationModal
        open
        title="Cancel this booking?"
        message="This action cannot be undone."
        confirmText="Yes, cancel booking"
        cancelText="Keep booking"
        onConfirm={vi.fn()}
        onCancel={vi.fn()}
      />,
    );

    expect(screen.getByRole("dialog")).toBeInTheDocument();

    expect(screen.getByText("Cancel this booking?")).toBeInTheDocument();
  });

  it("confirms cancellation", async () => {
    const user = userEvent.setup();
    const onConfirm = vi.fn();

    render(
      <ConfirmationModal
        open
        title="Cancel this booking?"
        message="This action cannot be undone."
        confirmText="Yes, cancel booking"
        cancelText="Keep booking"
        onConfirm={onConfirm}
        onCancel={vi.fn()}
      />,
    );

    await user.click(
      screen.getByRole("button", {
        name: "Yes, cancel booking",
      }),
    );

    expect(onConfirm).toHaveBeenCalledOnce();
  });

  it("keeps booking when cancel button clicked", async () => {
    const user = userEvent.setup();
    const onCancel = vi.fn();

    render(
      <ConfirmationModal
        open
        title="Cancel this booking?"
        message="This action cannot be undone."
        confirmText="Yes, cancel booking"
        cancelText="Keep booking"
        onConfirm={vi.fn()}
        onCancel={onCancel}
      />,
    );

    await user.click(
      screen.getByRole("button", {
        name: "Keep booking",
      }),
    );

    expect(onCancel).toHaveBeenCalledOnce();
  });

  it("closes using Escape", async () => {
    const user = userEvent.setup();
    const onCancel = vi.fn();

    render(
      <ConfirmationModal
        open
        title="Cancel this booking?"
        message="This action cannot be undone."
        onConfirm={vi.fn()}
        onCancel={onCancel}
      />,
    );

    await user.keyboard("{Escape}");

    expect(onCancel).toHaveBeenCalledOnce();
  });
});
