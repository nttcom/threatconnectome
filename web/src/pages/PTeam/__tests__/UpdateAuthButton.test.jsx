import { render, screen } from "@testing-library/react";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";

import { UpdateAuthButton } from "../UpdateAuthButton";

const mockTemplate = () => {
  throw new Error("Not implemented: You should override mock using vi.fn().");
};

describe("TestUpdateAuthButton", () => {
  const baseProps = {
    disabled: false,
    onUpdate: mockTemplate,
  };

  it("UpdateAuthButton is enabled if not disabled", () => {
    const testProps = { ...baseProps, disabled: false };
    render(<UpdateAuthButton {...testProps} />);

    const button = screen.getByRole("button");
    expect(button).toBeEnabled();
  });

  it("UpdateAuthButton is disabled if disabled", () => {
    const testProps = { ...baseProps, disabled: true };
    render(<UpdateAuthButton {...testProps} />);

    const button = screen.getByRole("button");
    expect(button).toBeDisabled();
  });

  it("UpdateAuthButton calls onUpdate if enabled and clicked", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    const mockOnUpdate = vi.fn(() => {});
    const testProps = { ...baseProps, disabled: false, onUpdate: mockOnUpdate };
    render(<UpdateAuthButton {...testProps} />);

    const button = screen.getByRole("button");
    await ue.click(button);

    expect(mockOnUpdate).toBeCalledTimes(1);
  });

  it("UpdateAuthButton does not call onUpdate if disabled and clicked", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    const mockOnUpdate = vi.fn(() => {});
    const testProps = { ...baseProps, disabled: true, onUpdate: mockOnUpdate };
    render(<UpdateAuthButton {...testProps} />);

    const button = screen.getByRole("button");
    await ue.click(button);

    expect(mockOnUpdate).toBeCalledTimes(0);
  });
});
