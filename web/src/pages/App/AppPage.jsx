import { Box } from "@mui/material";
import { onAuthStateChanged } from "firebase/auth";
import React, { useEffect } from "react";
import { ErrorBoundary } from "react-error-boundary";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { useTryLoginMutation } from "../../services/tcApi";
import { setAuthUserIsReady } from "../../slices/auth";
import Firebase from "../../utils/Firebase";
import { mainMaxWidth } from "../../utils/const";

import { AppBar } from "./AppBar";
import { AppFallback } from "./AppFallback";
import { Drawer } from "./Drawer";
import { Main } from "./Main";
import { OutletWithCheckedParams } from "./OutletWithCheckedParams";

export function App() {
  const system = useSelector((state) => state.system);
  const location = useLocation();
  const navigate = useNavigate();

  const dispatch = useDispatch();
  const [tryLogin] = useTryLoginMutation();

  useEffect(() => {
    onAuthStateChanged(Firebase.getAuth(), (user) => {
      if (!user) {
        navigate("/login", {
          state: {
            from: location.pathname,
            search: location.search,
            message: "Please login to continue.",
          },
        });
      } else {
        dispatch(setAuthUserIsReady(true));
      }
    });
  }, [location, dispatch, navigate, tryLogin]);

  return (
    <>
      <Box flexGrow={1}>
        <AppBar />
      </Box>
      <Drawer />
      <Main open={system.drawerOpen}>
        <Box display="flex" flexDirection="row" flexGrow={1} justifyContent="center" m={1}>
          <Box display="flex" flexDirection="column" flexGrow={1} maxWidth={mainMaxWidth}>
            <ErrorBoundary FallbackComponent={AppFallback}>
              <OutletWithCheckedParams />
            </ErrorBoundary>
          </Box>
        </Box>
      </Main>
    </>
  );
}
