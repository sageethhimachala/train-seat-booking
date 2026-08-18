import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import SearchForm from "./SearchForm";
import { stations } from "../test/testData";

describe("SearchForm", () => {
  it("renders origin and destination selectors", () => {
    render(
      <SearchForm stations={stations} loading={false} onSearch={vi.fn()} />,
    );

    expect(screen.getByText("Plan your journey")).toBeInTheDocument();

    expect(screen.getByLabelText("Origin station")).toBeInTheDocument();

    expect(screen.getByLabelText("Destination station")).toBeInTheDocument();
  });

  it("disables search until both stations are selected", () => {
    render(
      <SearchForm stations={stations} loading={false} onSearch={vi.fn()} />,
    );

    expect(
      screen.getByRole("button", {
        name: /search available seats/i,
      }),
    ).toBeDisabled();
  });

  it("does not allow the same station for origin and destination", async () => {
    const user = userEvent.setup();

    render(
      <SearchForm stations={stations} loading={false} onSearch={vi.fn()} />,
    );

    const origin = screen.getByLabelText("Origin station");

    const destination = screen.getByLabelText("Destination station");

    await user.selectOptions(origin, "1");

    const destinationOptions = Array.from(destination.options).map(
      (option) => option.value,
    );

    expect(destinationOptions).not.toContain("1");
  });

  it("submits selected station IDs", async () => {
    const user = userEvent.setup();
    const onSearch = vi.fn();

    render(
      <SearchForm stations={stations} loading={false} onSearch={onSearch} />,
    );

    await user.selectOptions(screen.getByLabelText("Origin station"), "1");

    await user.selectOptions(screen.getByLabelText("Destination station"), "3");

    await user.click(
      screen.getByRole("button", {
        name: /search available seats/i,
      }),
    );

    expect(onSearch).toHaveBeenCalledOnce();

    expect(onSearch).toHaveBeenCalledWith({
      originStationId: 1,
      destinationStationId: 3,
    });
  });

  it("swaps selected stations", async () => {
    const user = userEvent.setup();

    render(
      <SearchForm stations={stations} loading={false} onSearch={vi.fn()} />,
    );

    const origin = screen.getByLabelText("Origin station");

    const destination = screen.getByLabelText("Destination station");

    await user.selectOptions(origin, "1");
    await user.selectOptions(destination, "3");

    await user.click(
      screen.getByRole("button", {
        name: /swap origin and destination/i,
      }),
    );

    expect(origin).toHaveValue("3");
    expect(destination).toHaveValue("1");
  });
});
