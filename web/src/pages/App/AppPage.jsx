import { Box, useMediaQuery, useTheme } from "@mui/material";
import { useEffect } from "react";
import { ErrorBoundary } from "react-error-boundary";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../hooks/auth";
import { setAuthUserIsReady, setRedirectedFrom } from "../../slices/auth";
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
  const { onAuthStateChanged } = useAuth();

  useEffect(() => {
    const signInCallback = () => dispatch(setAuthUserIsReady(true));
    const signOutCallback = () => {
      dispatch(setAuthUserIsReady(false));
      navigate("/login", {
        state: {
          message: "Please login to continue.",
        },
      });
    };
    const unsubscribe = onAuthStateChanged({ signInCallback, signOutCallback });
    return () => unsubscribe(); // unsubscribe at unmounting.
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, []);

  useEffect(() => {
    dispatch(setRedirectedFrom({ from: location.pathname, search: location.search }));
  }, [dispatch, location.pathname, location.search]);

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  return (
    <>
      <Box flexGrow={1}>
        <AppBar />
      </Box>
      <Drawer />
      <Main open={!isMobile && system.drawerOpen}>
        <Box display="flex" flexDirection="row" flexGrow={1} justifyContent="center" m={1}>
          <Box display="flex" flexDirection="column" flexGrow={1} maxWidth={mainMaxWidth}>
            <ErrorBoundary FallbackComponent={AppFallback} resetKeys={[location.pathname]}>
              <OutletWithCheckedParams />
            </ErrorBoundary>
          </Box>
        </Box>
      </Main>
    </>
  );
}
