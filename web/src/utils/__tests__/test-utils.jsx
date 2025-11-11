import { render as rtlRender } from "@testing-library/react";
import { Provider } from "react-redux";
import { MemoryRouter } from "react-router-dom";

import { AuthProvider } from "../../providers/auth/AuthContext";
import store from "../../store";

const AllTheProviders = ({ children }) => {
  return (
    <Provider store={store}>
      <MemoryRouter>
        <AuthProvider>{children}</AuthProvider>
      </MemoryRouter>
    </Provider>
  );
};

const render = (ui, options) => {
  rtlRender(ui, { wrapper: AllTheProviders, ...options });
};

export * from "@testing-library/react";
export { render };
