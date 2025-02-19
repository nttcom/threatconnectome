import { render, screen } from "@testing-library/react";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";
import React from "react";
import { Provider, useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../../../hooks/auth";
import { AuthProvider } from "../../../providers/auth/AuthContext";
import { tcApi } from "../../../services/tcApi";
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
      expect(screen.getByRole("button", { name: "Logout" })).toBeEnabled();
      expect(screen.getByLabelText("menu")).toBeInTheDocument();
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
  describe("Logout Behavior", () => {
    it("resets API states and navigates to login when the Logout button is clicked", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const mockDispatch = vi.fn();
      vi.mocked(useDispatch).mockReturnValue(mockDispatch);

      const mockNavigate = vi.fn();
      vi.mocked(useNavigate).mockReturnValue(mockNavigate);

      const mockSignOut = vi.fn();
      useAuth.mockReturnValue({ signOut: mockSignOut });

      renderAppBar();
      await ue.click(screen.getByRole("button", { name: "Logout" }));

      expect(mockDispatch).toHaveBeenCalledWith(tcApi.util.resetApiState());
      expect(mockSignOut).toBeCalledTimes(1);
    });
  });
});
