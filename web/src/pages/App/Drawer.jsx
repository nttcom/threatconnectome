import { Groups as GroupsIcon, Home as HomeIcon, Topic as TopicIcon } from "@mui/icons-material";
import {
  Drawer as MuiDrawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { setDrawerOpen } from "../../slices/system";
import { LocationReader } from "../../utils/LocationReader";
import { drawerWidth, drawerParams } from "../../utils/const";

const DrawerHeader = styled("div")(({ theme }) => ({
  alignItems: "center",
  display: "flex",
  justifyContent: "center",
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
}));

export function Drawer() {
  const location = useLocation();
  const locationReader = new LocationReader(location);
  const navigate = useNavigate();

  const system = useSelector((state) => state.system);

  const StyledListItemIcon = styled(ListItemIcon)({
    color: "white",
  });

  const StyledListItemButton = styled(ListItemButton)({
    "&:hover": {
      backgroundColor: drawerParams.hoverColor,
    },
    "&.Mui-selected": {
      backgroundColor: drawerParams.hoverColor,
      "&:hover": {
        backgroundColor: drawerParams.hoverColor,
      },
    },
  });

  const queryParams = new URLSearchParams(location.search).toString();

  const handleNavigateTop = () => {
    navigate("/?" + queryParams);
  };

  const dispatch = useDispatch();
  const theme = useTheme();
  const isLgUp = useMediaQuery(theme.breakpoints.up("lg"));
  const isSmDown = useMediaQuery(theme.breakpoints.down("sm"));

  // --- Effects for responsive drawer behavior ---

  // Auto-open drawer on large screens.
  // HACK: Use async update to prevent UI freeze from Drawer's race condition.
  useEffect(() => {
    const timer = setTimeout(() => {
      dispatch(setDrawerOpen(isLgUp));
    }, 0);

    return () => {
      clearTimeout(timer);
    };
  }, [isLgUp, dispatch]);

  const drawerTitle = "Threatconnectome";

  return (
    <MuiDrawer
      anchor="left"
      open={system.drawerOpen}
      variant={isSmDown ? "temporary" : "persistent"}
      onClose={() => dispatch(setDrawerOpen(false))}
      sx={{
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          boxSizing: "border-box",
          width: drawerWidth,
        },
      }}
      PaperProps={{
        sx: {
          backgroundColor: drawerParams.mainColor,
          color: "white",
        },
      }}
    >
      <DrawerHeader>
        <Typography onClick={handleNavigateTop} variant="h7" sx={{ fontWeight: 700 }}>
          {drawerTitle}
        </Typography>
      </DrawerHeader>
      <List>
        <>
          <StyledListItemButton
            onClick={() => navigate("/?" + queryParams)}
            selected={locationReader.isStatusPage()}
          >
            <StyledListItemIcon>
              <HomeIcon />
            </StyledListItemIcon>
            <ListItemText>Status</ListItemText>
          </StyledListItemButton>
          <StyledListItemButton
            onClick={() => navigate("/pteam?" + queryParams)}
            selected={locationReader.isPTeamPage()}
          >
            <StyledListItemIcon>
              <GroupsIcon />
            </StyledListItemIcon>
            <ListItemText>Team</ListItemText>
          </StyledListItemButton>
        </>
        {/* Vulns */}
        <StyledListItemButton
          onClick={() => navigate("/vulns?" + queryParams)}
          selected={locationReader.isVulnsPage()}
        >
          <StyledListItemIcon>
            <TopicIcon />
          </StyledListItemIcon>
          <ListItemText>Vulns</ListItemText>
        </StyledListItemButton>
        {/* Vulnerabilities -- not listed on drawer, currently */}
      </List>
    </MuiDrawer>
  );
}
