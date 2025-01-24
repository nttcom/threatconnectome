import { render, screen } from "@testing-library/react";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";
import React from "react";

import { AuthAdminCheckbox } from "../AuthAdminCheckbox";

const mockTemplate = () => {
  throw new Error("Not implemented: You should override mock using vi.fn().");
};

describe("TestAuthAdminCheckbox", () => {
  const baseProps = {
    checked: false,
    editable: false,
    modified: false,
    onChange: mockTemplate,
  };

  it("AuthAdminCheckbox is enabled if editable", () => {
    const testProps = { ...baseProps, editable: true };
    render(<AuthAdminCheckbox {...testProps} />);

    const checkbox = screen.getByRole("checkbox");
    expect(checkbox).toBeEnabled();
  });

  it("AuthAdminCheckbox is disabled if not editable", () => {
    const testProps = { ...baseProps, editable: false };
    render(<AuthAdminCheckbox {...testProps} />);

    const checkbox = screen.getByRole("checkbox");
    expect(checkbox).toBeDisabled();
  });

  it("AuthAdminCheckbox is checked if checked", () => {
    const testProps = { ...baseProps, checked: true };
    render(<AuthAdminCheckbox {...testProps} />);

    const checkbox = screen.getByRole("checkbox");
    expect(checkbox).toBeChecked();
  });

  it("AuthAdminCheckbox is not checked if not checked", () => {
    const testProps = { ...baseProps, checked: false };
    render(<AuthAdminCheckbox {...testProps} />);

    const checkbox = screen.getByRole("checkbox");
    expect(checkbox).not.toBeChecked();
  });

  it("AuthAdminCheckbox prints * if modified", () => {
    const testProps = { ...baseProps, modified: true };
    render(<AuthAdminCheckbox {...testProps} />);

    const asterisk = screen.getByText("*");
    expect(asterisk).toBeDefined();
  });

  it("AuthAdminCheckbox does not print * if not modified", () => {
    const testProps = { ...baseProps, modified: false };
    render(<AuthAdminCheckbox {...testProps} />);

    const asterisk = screen.queryByText("*"); // use queryBy to expect inexistence
    expect(asterisk).toBeNull();
  });

  it("AuthAdminCheckbox calls onChange when editable and clicked", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    const mockOnChange = vi.fn();
    const testProps = { ...baseProps, editable: true, onChange: mockOnChange };
    render(<AuthAdminCheckbox {...testProps} />);

    const checkbox = screen.getByRole("checkbox");
    await ue.click(checkbox);

    expect(mockOnChange).toBeCalledTimes(1);
  });

  it("AuthAdminCheckbox not calls onChange when disabled and clicked", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    const mockOnChange = vi.fn(() => {});
    const testProps = { ...baseProps, editable: false, onChange: mockOnChange };
    render(<AuthAdminCheckbox {...testProps} />);

    const checkbox = screen.getByRole("checkbox");
    await ue.click(checkbox);

    expect(mockOnChange).toBeCalledTimes(0);
  });
});
