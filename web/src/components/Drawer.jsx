import {
  AccountCircle as AccountCircleIcon,
  Assessment as AssessmentIcon,
  Square as SquareIcon,
  Groups as GroupsIcon,
  Home as HomeIcon,
} from "@mui/icons-material";
import {
  Drawer as MuiDrawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import React from "react";
import { useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { drawerWidth, teamColor } from "../utils/const";

const DrawerHeader = styled("div")(({ theme }) => ({
  alignItems: "center",
  display: "flex",
  justifyContent: "center",
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
}));

export default function Drawer() {
  const location = useLocation();
  const navigate = useNavigate();

  const system = useSelector((state) => state.system);

  const StyledListItemIcon = styled(ListItemIcon)({
    color: "white",
  });

  const StyledListItemButton = styled(ListItemButton)({
    "&:hover": {
      backgroundColor: teamColor[system.teamMode].hoverColor,
    },
    "&.Mui-selected": {
      backgroundColor: teamColor[system.teamMode].hoverColor,
      "&:hover": {
        backgroundColor: teamColor[system.teamMode].hoverColor,
      },
    },
  });

  const queryParams = new URLSearchParams(location.search).toString();

  const handleNavigateTop = () => {
    if (system.teamMode === "pteam") {
      navigate("/?" + queryParams);
    } else if (system.teamMode === "ateam") {
      navigate("/analysis?" + queryParams);
    } else if (system.teamMode === "gteam") {
      navigate("/zone?" + queryParams);
    }
  };

  const drawerTitle = "Threatconnectome";

  return (
    <MuiDrawer
      anchor="left"
      open={system.drawerOpen}
      variant="persistent"
      sx={{
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          boxSizing: "border-box",
          width: drawerWidth,
        },
      }}
      PaperProps={{
        sx: {
          backgroundColor: teamColor[system.teamMode].mainColor,
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
        {system.teamMode === "pteam" && (
          <>
            <StyledListItemButton
              onClick={() => navigate("/?" + queryParams)}
              selected={location.pathname === "/"}
            >
              <StyledListItemIcon>
                <HomeIcon />
              </StyledListItemIcon>
              <ListItemText>Status</ListItemText>
            </StyledListItemButton>
            <StyledListItemButton
              onClick={() => navigate("/pteam?" + queryParams)}
              selected={location.pathname === "/pteam"}
            >
              <StyledListItemIcon>
                <GroupsIcon />
              </StyledListItemIcon>
              <ListItemText>PTeam</ListItemText>
            </StyledListItemButton>
          </>
        )}
        {system.teamMode === "ateam" && (
          <>
            <StyledListItemButton
              onClick={() => navigate("/analysis?" + queryParams)}
              selected={location.pathname === "/analysis"}
            >
              <StyledListItemIcon>
                <AssessmentIcon />
              </StyledListItemIcon>
              <ListItemText>Analysis</ListItemText>
            </StyledListItemButton>
            <StyledListItemButton
              onClick={() => navigate("/ateam?" + queryParams)}
              selected={location.pathname === "/ateam"}
            >
              <StyledListItemIcon>
                <GroupsIcon />
              </StyledListItemIcon>
              <ListItemText>ATeam</ListItemText>
            </StyledListItemButton>
          </>
        )}
        {system.teamMode === "gteam" && (
          <>
            <StyledListItemButton
              onClick={() => navigate("/zone?" + queryParams)}
              selected={location.pathname === "/zone"}
            >
              <StyledListItemIcon>
                <SquareIcon />
              </StyledListItemIcon>
              <ListItemText>Zone</ListItemText>
            </StyledListItemButton>
            <StyledListItemButton
              onClick={() => navigate("/gteam?" + queryParams)}
              selected={location.pathname === "/gteam"}
            >
              <StyledListItemIcon>
                <GroupsIcon />
              </StyledListItemIcon>
              <ListItemText>GTeam</ListItemText>
            </StyledListItemButton>
          </>
        )}
        <StyledListItemButton
          onClick={() => navigate("/account?" + queryParams)}
          selected={location.pathname === "/account"}
        >
          <StyledListItemIcon>
            <AccountCircleIcon />
          </StyledListItemIcon>
          <ListItemText>Account</ListItemText>
        </StyledListItemButton>
      </List>
    </MuiDrawer>
  );
}
