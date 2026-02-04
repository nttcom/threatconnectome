import { Menu as MenuIcon } from "@mui/icons-material";
import {
  AppBar as MuiAppBar,
  Box,
  Divider,
  IconButton,
  Toolbar,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import { ErrorBoundary } from "react-error-boundary";
import { useDispatch, useSelector } from "react-redux";

import { setDrawerOpen } from "../../slices/system";
import { drawerWidth } from "../../utils/const";

import { AppFallback } from "./AppFallback";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { TeamSelector } from "./TeamSelector";
import { UserMenu } from "./UserMenu/UserMenu";

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

  const handleDrawerOpen = () => dispatch(setDrawerOpen(!system.drawerOpen));
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  return (
    <>
      <StyledAppBar open={!isMobile && system.drawerOpen} position="fixed">
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
          <ErrorBoundary FallbackComponent={AppFallback}>
            <TeamSelector />
          </ErrorBoundary>
          <Box flexGrow={1} />
          <LanguageSwitcher />
          <UserMenu />
        </Toolbar>
      </StyledAppBar>
      <Toolbar />
    </>
  );
}
