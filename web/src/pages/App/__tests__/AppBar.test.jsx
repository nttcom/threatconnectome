import { render, screen } from "@testing-library/react";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";
import React from "react";
import { Provider, useDispatch } from "react-redux";

import { useAuth } from "../../../hooks/auth";
import { AuthProvider } from "../../../providers/auth/AuthContext";

import { setDrawerOpen } from "../../../slices/system";
import store from "../../../store";
import { AppBar } from "../AppBar";

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: vi.fn(),
    useLocation: vi.fn(),
  };
});

vi.mock("react-redux", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useDispatch: vi.fn(),
  };
});

vi.mock("../../../hooks/auth", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useAuth: vi.fn(),
  };
});

vi.mock("../UserMenu/UserMenu", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    UserMenu: () => <div data-testid="user-menu">UserMenu</div>,
  };
});

const renderAppBar = () => {
  render(
    <Provider store={store}>
      <AuthProvider>
        <AppBar />
      </AuthProvider>
    </Provider>,
  );
};

describe("TestAppBar", () => {
  describe("Rendering", () => {
    it("AppBar renders", () => {
      const mockSignOut = vi.fn();
      useAuth.mockReturnValue({ signOut: mockSignOut });

      renderAppBar();

      expect(screen.getByLabelText("menu")).toBeInTheDocument();
      expect(screen.getByText("UserMenu")).toBeInTheDocument();
    });
  });
  describe("Drawer Behavior", () => {
    it("opens the drawer when the menu button is clicked", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const mockDispatch = vi.fn();
      vi.mocked(useDispatch).mockReturnValue(mockDispatch);

      const mockSignOut = vi.fn();
      useAuth.mockReturnValue({ signOut: mockSignOut });

      renderAppBar();

      await ue.click(screen.getByLabelText("menu"));
      expect(mockDispatch).toHaveBeenCalledWith(setDrawerOpen(expect.any(Boolean)));
    });
  });
});
