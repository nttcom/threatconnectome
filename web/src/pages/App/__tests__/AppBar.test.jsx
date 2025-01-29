import { render, screen } from "@testing-library/react";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";
import React from "react";
import { Provider, useDispatch } from "react-redux";
import { BrowserRouter, useNavigate } from "react-router-dom";

import { firebaseApi } from "../../../services/firebaseApi";
import { tcApi } from "../../../services/tcApi";
import { setDrawerOpen } from "../../../slices/system";
import store from "../../../store";
import { AppBar } from "../AppBar";

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: vi.fn(),
  };
});

vi.mock("react-redux", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useDispatch: vi.fn(),
  };
});

const renderAppBar = () => {
  render(
    <Provider store={store}>
      <BrowserRouter>
        <AppBar />
      </BrowserRouter>
    </Provider>,
  );
};

describe("TestAppBar", () => {
  describe("Rendering", () => {
    it("AppBar renders", () => {
      renderAppBar();
      expect(screen.getByRole("button", { name: "Logout" })).toBeEnabled();
      expect(screen.getByLabelText("menu")).toBeInTheDocument();
    });
  });
  describe("Drawer Behavior", () => {
    it("opens the drawer when the menu button is clicked", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const dispatchMock = vi.fn();
      vi.mocked(useDispatch).mockReturnValue(dispatchMock);

      renderAppBar();
      await ue.click(screen.getByLabelText("menu"));

      expect(dispatchMock).toHaveBeenCalledWith(setDrawerOpen(expect.any(Boolean)));
    });
  });
  describe("Logout Behavior", () => {
    it("resets API states and navigates to login when the Logout button is clicked", async () => {
      const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
      const dispatchMock = vi.fn();
      vi.mocked(useDispatch).mockReturnValue(dispatchMock);

      const navigateMock = vi.fn();
      vi.mocked(useNavigate).mockReturnValue(navigateMock);

      renderAppBar();
      await ue.click(screen.getByRole("button", { name: "Logout" }));

      expect(dispatchMock).toHaveBeenCalledWith(firebaseApi.util.resetApiState());
      expect(dispatchMock).toHaveBeenCalledWith(tcApi.util.resetApiState());

      expect(navigateMock).toHaveBeenCalledWith("/login", {
        state: { message: "Logged out successfully.", from: null, search: null },
      });
    });
  });
});
