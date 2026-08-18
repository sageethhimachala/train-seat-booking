import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import CopyButton from "./CopyButton";

describe("CopyButton", () => {
  beforeEach(() => {
    Object.defineProperty(window, "isSecureContext", {
      configurable: true,
      value: true,
    });
  });

  it("copies supplied value", async () => {
    const user = userEvent.setup();

    const writeTextSpy = vi.spyOn(navigator.clipboard, "writeText");

    render(<CopyButton value="TRN-ABC12345" label="Copy reference" />);

    await user.click(
      screen.getByRole("button", {
        name: "Copy reference",
      }),
    );

    expect(writeTextSpy).toHaveBeenCalledWith("TRN-ABC12345");
  });

  it("shows copied message after success", async () => {
    const user = userEvent.setup();

    render(<CopyButton value="TRN-ABC12345" label="Copy reference" />);

    await user.click(
      screen.getByRole("button", {
        name: "Copy reference",
      }),
    );

    expect(await screen.findByText("Copied ✓")).toBeInTheDocument();
  });
});
