import { configureStore } from "@reduxjs/toolkit";
import { render as rtlRender } from "@testing-library/react";
import { Provider } from "react-redux";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { AuthProvider } from "../../providers/auth/AuthContext";
import { tcApi } from "../../services/tcApi";
import { sliceReducers } from "../../slices";

const render = (
  ui,
  {
    preloadedState = { auth: { authUserIsReady: true } },
    store = configureStore({
      reducer: {
        ...sliceReducers,
        [tcApi.reducerPath]: tcApi.reducer,
      },
      middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(tcApi.middleware),
      // preloadedState,
    }),

    route = "/",
    path = "/",
    ...options
  } = {},
) => {
  const AllTheProviders = ({ children }) => {
    return (
      <Provider store={store}>
        <MemoryRouter initialEntries={[route]}>
          <AuthProvider>
            <Routes>
              <Route path={path} element={children} />
            </Routes>
          </AuthProvider>
        </MemoryRouter>
      </Provider>
    );
  };
  return rtlRender(ui, { wrapper: AllTheProviders, ...options });
};

export * from "@testing-library/react";
export { render };
