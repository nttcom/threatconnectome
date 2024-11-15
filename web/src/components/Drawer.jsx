import {
  AccountCircle as AccountCircleIcon,
  Assessment as AssessmentIcon,
  Groups as GroupsIcon,
  Home as HomeIcon,
  Topic as TopicIcon,
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

import { LocationReader } from "../utils/LocationReader";
import { drawerWidth, teamColor } from "../utils/const";

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
      backgroundColor: teamColor[locationReader.getTeamMode()].hoverColor,
    },
    "&.Mui-selected": {
      backgroundColor: teamColor[locationReader.getTeamMode()].hoverColor,
      "&:hover": {
        backgroundColor: teamColor[locationReader.getTeamMode()].hoverColor,
      },
    },
  });

  const queryParams = new URLSearchParams(location.search).toString();

  const handleNavigateTop = () => {
    if (locationReader.isPTeamMode()) {
      navigate("/?" + queryParams);
    } else if (locationReader.isATeamMode()) {
      navigate("/analysis?" + queryParams);
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
          backgroundColor: teamColor[locationReader.getTeamMode()].mainColor,
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
        {locationReader.isPTeamMode() && (
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
              <ListItemText>PTeam</ListItemText>
            </StyledListItemButton>
          </>
        )}
        {locationReader.isATeamMode() && (
          <>
            <StyledListItemButton
              onClick={() => navigate("/analysis?" + queryParams)}
              selected={locationReader.isAnalysisPage()}
            >
              <StyledListItemIcon>
                <AssessmentIcon />
              </StyledListItemIcon>
              <ListItemText>Analysis</ListItemText>
            </StyledListItemButton>
            <StyledListItemButton
              onClick={() => navigate("/ateam?" + queryParams)}
              selected={locationReader.isATeamPage()}
            >
              <StyledListItemIcon>
                <GroupsIcon />
              </StyledListItemIcon>
              <ListItemText>ATeam</ListItemText>
            </StyledListItemButton>
          </>
        )}
        {/* Topics */}
        <StyledListItemButton
          onClick={() => navigate("/topics?" + queryParams)}
          selected={locationReader.isTopicsPage()}
        >
          <StyledListItemIcon>
            <TopicIcon />
          </StyledListItemIcon>
          <ListItemText>Topics</ListItemText>
        </StyledListItemButton>
        {/* Account */}
        <StyledListItemButton
          onClick={() => navigate("/account?" + queryParams)}
          selected={locationReader.isAccountPage()}
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
