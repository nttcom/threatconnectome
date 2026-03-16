import { Menu as MenuIcon } from "@mui/icons-material";
import {
  AppBar as MuiAppBar,
  Box,
  IconButton,
  Toolbar,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import { ErrorBoundary } from "react-error-boundary";
import { useDispatch, useSelector } from "react-redux";

import { LanguageSwitcher } from "../../components/LanguageSwitcher";
import { setDrawerOpen } from "../../slices/system";
import { drawerWidth } from "../../utils/const";

import { AppFallback } from "./AppFallback";
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
            sx={{ mr: { xs: 0, sm: 1 } }}
          >
            <MenuIcon />
          </IconButton>
          <Box
            sx={{
              pr: { xs: 0, md: 1 },
              flexGrow: { xs: 1, md: 0 },
              minWidth: 0,
              maxWidth: "350px",
            }}
          >
            <ErrorBoundary FallbackComponent={AppFallback}>
              <TeamSelector />
            </ErrorBoundary>
          </Box>
          <Box flexGrow={1} />
          <Box sx={{ display: "flex", flexShrink: 0 }}>
            <LanguageSwitcher />
            <UserMenu />
          </Box>
        </Toolbar>
      </StyledAppBar>
      <Toolbar />
    </>
  );
}
