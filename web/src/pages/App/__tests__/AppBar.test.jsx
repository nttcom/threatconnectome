import { render, screen } from "@testing-library/react";
import userEvent, { PointerEventsCheckLevel } from "@testing-library/user-event";
import React from "react";
import { Provider, useDispatch } from "react-redux";
import { BrowserRouter, useNavigate } from "react-router-dom";
//import { vi } from "vitest";

import { firebaseApi } from "../../../services/firebaseApi";
import { tcApi } from "../../../services/tcApi";
import { setDrawerOpen } from "../../../slices/system";
import store from "../../../store";
import { AppBar } from "../AppBar";

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: vi.fn(),
  };
});

vi.mock("react-redux", async () => {
  const actual = await vi.importActual("react-redux");
  return {
    ...actual,
    useDispatch: vi.fn(),
  };
});

const renderAppBar = () => {
  render(
    <Provider store={store}>
      <BrowserRouter
        future={{
          /* to prevent React Router Future Flag Warning.
           * see https://reactrouter.com/v6/upgrading/future#v7_relativesplatpath for details.
           */
          // v7_fetcherPersist: true,
          // v7_normalizeFormMethod: true,
          // v7_partialHydration: true,
          v7_relativeSplatPath: true,
          // v7_skipActionErrorRevalidation: true,
          v7_startTransition: true,
        }}
      >
        <AppBar />
      </BrowserRouter>
    </Provider>,
  );
};

describe("TestAppBar", () => {
  it("AppBar renders", () => {
    renderAppBar();
    const tmp = screen.getByRole("button", { name: "Logout" });
    expect(tmp).toBeEnabled();
    expect(screen.getByLabelText("menu")).toBeInTheDocument();
  });

  it("toggles drawer state when menu button is clicked", async () => {
    const ue = userEvent.setup({ pointerEventsCheck: PointerEventsCheckLevel.Never });
    const dispatchMock = vi.fn();
    vi.mocked(useDispatch).mockReturnValue(dispatchMock);

    renderAppBar();
    await ue.click(screen.getByLabelText("menu"));

    expect(dispatchMock).toHaveBeenCalledWith(setDrawerOpen(expect.any(Boolean)));
  });

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
