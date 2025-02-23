import { Menu as MenuIcon } from "@mui/icons-material";
import { AppBar as MuiAppBar, Box, Button, Divider, IconButton, Toolbar } from "@mui/material";
import { styled } from "@mui/material/styles";
import React from "react";
import { ErrorBoundary } from "react-error-boundary";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../../hooks/auth";
import { tcApi } from "../../services/tcApi";
import { setAuthUserIsReady, setRedirectedFrom } from "../../slices/auth";
import { setDrawerOpen } from "../../slices/system";
import { drawerWidth } from "../../utils/const";

import { AppFallback } from "./AppFallback";
import { TeamSelector } from "./TeamSelector";

const StyledAppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== "open",
})(({ theme, open }) => ({
  transition: theme.transitions.create(["margin", "width"], {
    duration: theme.transitions.duration.leavingScreen,
    easing: theme.transitions.easing.sharp,
  }),
  ...(open && {
    marginLeft: `${drawerWidth}px`,
    transition: theme.transitions.create(["margin", "width"], {
      duration: theme.transitions.duration.enteringScreen,
      easing: theme.transitions.easing.easeOut,
    }),
    width: `calc(100% - ${drawerWidth}px)`,
  }),
  color: "black",
  backgroundColor: "white",
  boxShadow: "initial",
  borderBottom: "1px solid #E0E0E0",
}));

export function AppBar() {
  const dispatch = useDispatch();
  const system = useSelector((state) => state.system);

  const navigate = useNavigate();
  const { signOut } = useAuth();

  const handleDrawerOpen = () => dispatch(setDrawerOpen(!system.drawerOpen));

  const handleLogout = async () => {
    dispatch(tcApi.util.resetApiState()); // reset RTKQ
    dispatch(setAuthUserIsReady(false));
    dispatch(setRedirectedFrom({}));
    await signOut();
  };

  return (
    <>
      <StyledAppBar open={system.drawerOpen} position="fixed">
        <Toolbar>
          <IconButton
            aria-label="menu"
            color="inherit"
            edge="start"
            size="large"
            onClick={handleDrawerOpen}
            sx={{ mr: 1.5 }}
          >
            <MenuIcon />
          </IconButton>
          <Divider orientation="vertical" flexItem sx={{ mr: 2 }} />
          <Box flexGrow={1} />
          <ErrorBoundary FallbackComponent={AppFallback}>
            <TeamSelector />
          </ErrorBoundary>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </StyledAppBar>
      <Toolbar />
    </>
  );
}
