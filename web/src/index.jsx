import { CssBaseline } from "@mui/material";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { SnackbarProvider } from "notistack";
import React from "react";
import { CookiesProvider } from "react-cookie";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import { BrowserRouter as Router, Navigate, Route, Routes } from "react-router-dom";

import {
  AcceptATeamInvitation,
  AcceptATeamWatchingRequest,
  AcceptGTeamInvitation,
  AcceptPTeamInvitation,
  Account,
  Analysis,
  App,
  ATeam,
  GTeam,
  Login,
  ResetPassword,
  Status,
  Tag,
  PTeam,
  Zone,
  ZoneEdit,
} from "./pages";
import store from "./store";

const container = document.getElementById("root");
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <CookiesProvider>
      <Provider store={store}>
        <ThemeProvider theme={createTheme()}>
          <CssBaseline />
          <SnackbarProvider
            maxSnack={3}
            preventDuplicate={true}
            anchorOrigin={{ horizontal: "center", vertical: "top" }}
            autoHideDuration={5000}
          >
            <Router basename={process.env.PUBLIC_URL}>
              <Routes>
                <Route exact path="/login" element={<Login />} />
                <Route path="/reset_password" element={<ResetPassword />} />
                <Route path="/" element={<App />}>
                  <Route index element={<Status />} />
                  <Route path="account">
                    <Route index element={<Account />} />
                  </Route>
                  <Route path="pteam">
                    <Route index element={<PTeam />} />
                    <Route path="join" element={<AcceptPTeamInvitation />} />
                    <Route path="watching_request" element={<AcceptATeamWatchingRequest />} />
                  </Route>
                  <Route path="ateam">
                    <Route index element={<ATeam />} />
                    <Route path="join" element={<AcceptATeamInvitation />} />
                  </Route>
                  <Route path="gteam">
                    <Route index element={<GTeam />} />
                    <Route path="join" element={<AcceptGTeamInvitation />} />
                  </Route>
                  <Route path="zone">
                    <Route index element={<Zone />} />
                    <Route index path=":zoneName" element={<ZoneEdit />} />
                  </Route>
                  <Route path="zoneedit">
                    <Route index element={<ZoneEdit />} />
                  </Route>
                  <Route path="tags">
                    <Route index element={<Navigate to="/" />} />
                    <Route path=":tagId" element={<Tag />} />
                  </Route>
                  <Route path="*" element={<Navigate to="/" />} />
                  <Route path="analysis">
                    <Route index element={<Analysis />} />
                  </Route>
                </Route>
              </Routes>
            </Router>
          </SnackbarProvider>
        </ThemeProvider>
      </Provider>
    </CookiesProvider>
  </React.StrictMode>
);
