import { CssBaseline } from "@mui/material";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { SnackbarProvider } from "notistack";
import React from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import { BrowserRouter as Router, Navigate, Route, Routes } from "react-router-dom";

import {
  AcceptPTeamInvitation,
  Account,
  App,
  EmailVerification,
  Login,
  ResetPassword,
  Status,
  SignUp,
  Tag,
  TopicDetail,
  TopicManagement,
  PTeam,
} from "./pages";
import { AuthProvider } from "./providers/auth/AuthContext";
import store from "./store";

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
                <Route path="/reset_password" element={<ResetPassword />} />
                <Route path="/sign_up" element={<SignUp />} />
                <Route path="/email_verification" element={<EmailVerification />} />
                <Route path="/" element={<App />}>
                  <Route index element={<Status />} />
                  <Route path="account">
                    <Route index element={<Account />} />
                  </Route>
                  <Route path="pteam">
                    <Route index element={<PTeam />} />
                    <Route path="join" element={<AcceptPTeamInvitation />} />
                  </Route>
                  <Route path="tags">
                    <Route index element={<Navigate to="/" />} />
                    <Route path=":tagId" element={<Tag />} />
                  </Route>
                  <Route path="*" element={<Navigate to="/" />} />
                  <Route path="topics">
                    <Route index element={<TopicManagement />} />
                    <Route path=":topicId" element={<TopicDetail />} />
                  </Route>
                </Route>
              </Routes>
            </Router>
          </AuthProvider>
        </SnackbarProvider>
      </ThemeProvider>
    </Provider>
  </React.StrictMode>,
);
