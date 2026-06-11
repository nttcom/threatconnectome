import { render } from "@testing-library/react";

import { MenuShell } from "../Topbar/MenuShell";

const { menuMock } = vi.hoisted(() => ({
  menuMock: vi.fn(),
}));

vi.mock("@mui/material", () => ({
  Menu: (props) => {
    menuMock(props);
    return <div>{props.children}</div>;
  },
}));

describe("MenuShell", () => {
  beforeEach(() => {
    menuMock.mockClear();
  });

  it("uses the responsive width value for Paper maxWidth", () => {
    const width = { xs: "calc(100vw - 16px)", sm: 336 };

    render(
      <MenuShell anchorEl={null} ariaLabel="Page menu" open onClose={vi.fn()} width={width}>
        <span>Menu item</span>
      </MenuShell>,
    );

    expect(menuMock).toHaveBeenCalledWith(
      expect.objectContaining({
        slotProps: expect.objectContaining({
          paper: expect.objectContaining({
            sx: expect.objectContaining({
              width,
              maxWidth: width,
            }),
          }),
        }),
      }),
    );
  });
});
