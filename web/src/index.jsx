import "@fontsource/roboto/300.css";
import "@fontsource/roboto/400.css";
import "@fontsource/roboto/500.css";
import "@fontsource/roboto/700.css";

import { CssBaseline } from "@mui/material";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { SnackbarProvider } from "notistack";
import React from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import { BrowserRouter as Router, Navigate, Route, Routes } from "react-router-dom";

import {
  AcceptPTeamInvitation,
  App,
  AuthKeycloakCallback,
  EmailVerification,
  Login,
  ResetPassword,
  Status,
  SignUp,
  Package,
  VulnDetail,
  VulnManagement,
  PTeam,
  ToDo,
} from "./pages";
import { ProductEolDetail } from "./pages/Eol/ProductEolDetailPage";
import { ProductEolList } from "./pages/Eol/ProductEolListPage";
import { ServiceEolDashboard } from "./pages/Eol/ServiceEolDashboardPage";
import { AuthProvider } from "./providers/auth/AuthContext";
import store from "./store";
import "./i18n/config.ts";

const container = document.getElementById("root");
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <Provider store={store}>
      <ThemeProvider theme={createTheme()}>
        <CssBaseline />
        <SnackbarProvider
          maxSnack={3}
          preventDuplicate={true}
          anchorOrigin={{ horizontal: "center", vertical: "top" }}
          autoHideDuration={5000}
        >
          <AuthProvider>
            <Router
              basename={import.meta.env.VITE_PUBLIC_URL}
              future={{
                /* to prevent React Router Future Flag Warning.
                 * see https://reactrouter.com/v6/upgrading/future#v7_relativesplatpath for details.
                 */
                v7_startTransition: true,
                v7_relativeSplatPath: true,
              }}
            >
              <Routes>
                <Route exact path="/login" element={<Login />} />
                <Route path="/auth_keycloak_callback" element={<AuthKeycloakCallback />} />
                <Route path="/email_verification" element={<EmailVerification />} />
                <Route path="/reset_password" element={<ResetPassword />} />
                <Route path="/sign_up" element={<SignUp />} />
                <Route path="/" element={<App />}>
                  <Route index element={<Status />} />
                  <Route path="pteam">
                    <Route index element={<PTeam />} />
                    <Route path="join" element={<AcceptPTeamInvitation />} />
                  </Route>
                  <Route path="packages">
                    <Route index element={<Navigate to="/" />} />
                    <Route path=":packageId" element={<Package />} />
                  </Route>
                  <Route path="*" element={<Navigate to="/" />} />
                  <Route path="vulns">
                    <Route index element={<VulnManagement />} />
                    <Route path=":vulnId" element={<VulnDetail />} />
                  </Route>
                  <Route path="todo">
                    <Route index element={<ToDo />} />
                  </Route>
                  <Route path="/eol" element={<ServiceEolDashboard />} />
                  <Route path="/supported-products" element={<ProductEolList />} />
                  <Route path="/supported-products/:productId" element={<ProductEolDetail />} />
                </Route>
              </Routes>
            </Router>
          </AuthProvider>
        </SnackbarProvider>
      </ThemeProvider>
    </Provider>
  </React.StrictMode>,
);
